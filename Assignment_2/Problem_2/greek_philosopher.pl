
% greek_philosopher.pl
% Resolution refutation of: "Socrates is mortal"




% Step 1: (FOL)

% English facts:
% 1. All men are mortal.
% 2. All Greeks are men.
% 3. All philosophers are thinkers.
% 4. Socrates is a Greek and a philosopher.
% We represent them as readable Prolog terms for the transformation pipeline.
step1_fol([
    forall(X, implies(man(X), mortal(X))),
    forall(X, implies(greek(X), man(X))),
    forall(X, implies(philosopher(X), thinker(X))),
    atomic(greek(socrates)),
    atomic(philosopher(socrates))
]).


% Step 2: Negation of the goal 

% Goal: mortal(socrates). For refutation we add its negation.
step2_negated_goal(not(mortal(socrates))).


% Step 3: Implication removal

% Replace (A -> B) by (not A) v B; keep quantifiers explicit here.
step3_implication_removed([
    forall(X, or(not(man(X)), mortal(X))),
    forall(X, or(not(greek(X)), man(X))),
    forall(X, or(not(philosopher(X)), thinker(X))),
    atomic(greek(socrates)),
    atomic(philosopher(socrates)),
    not(mortal(socrates))
]).


% Step 4:  (NNF)

% For this knowledge base negations already apply to atoms; pass-through.
step4_negation_moved(Clauses) :- step3_implication_removed(Clauses).


% Step 5: Standardization (rename bound variables to avoid clashes)

% Here we copy terms to ensure variable freshness in after processing.
step5_standardized(Standardized) :-
    step4_negation_moved(Clauses),
    findall(Copy, (member(C, Clauses), copy_term(C, Copy)), Standardized).


% Step 6: Skolemization

% There are no existential quantifiers in this KB, so skolemization makes no change.
step6_skolemized(Skolemized) :- step5_standardized(Skolemized).


% Step 7: CNF clauses 
% Positive literal: pred(...)
% Negative literal: neg(pred(...))

step7_cnf_clauses([
    [neg(man(X)), mortal(X)],            % from forall X: (not man(X) or mortal(X))
    [neg(greek(X)), man(X)],             % from forall X: (not greek(X) or man(X))
    [neg(philosopher(X)), thinker(X)],   % from forall X: (not philosopher(X) or thinker(X))
    [greek(socrates)],
    [philosopher(socrates)],
    [neg(mortal(socrates))]              % negated goal
]).


% Utility printer for steps
print_step(Title, Term) :-
    nl, write('--- '), write(Title), write(' ---'), nl,
    portray_clause(Term).

show_all_steps :-
    step1_fol(S1), print_step('Step 1: FOL representation', S1),
    step2_negated_goal(GN), print_step('Step 2: Negation of goal', GN),
    step3_implication_removed(S3), print_step('Step 3: After implication removal', S3),
    step4_negation_moved(S4), print_step('Step 4: Negation movement (NNF)', S4),
    step5_standardized(S5), print_step('Step 5: Standardized', S5),
    step6_skolemized(S6), print_step('Step 6: Skolemized', S6),
    step7_cnf_clauses(CNF), nl, write('--- Step 7: CNF clauses ---'), nl,
    forall(member(C, CNF), portray_clause(C)), nl.


% Step 8: Resolution implementation and execution
% A simple first-order resolution (with variable standardization via copy_term)


:- dynamic(my_clause/1).

load_cnf_into_db :-
    retractall(my_clause(_)),
    step7_cnf_clauses(Clauses),
    forall(member(C, Clauses), (copy_term(C, Ccpy), assertz(my_clause(Ccpy)))).

% complementary(Lit1, Lit2) holds when Lit1 and Lit2 are complementary (one negated)
complementary(neg(A), A).
complementary(A, neg(A)).

% resolve_pair(C1, C2, Resolvent)
% Try to resolve C1 and C2 on a complementary literal and return Resolvent
resolve_pair(C1, C2, Resolvent) :-
    member(L1, C1),
    member(L2, C2),
    complementary(L1, L2),
    % use fresh copies to avoid variable capture
    copy_term((C1,C2,L1,L2), (C1c,C2c,L1c,L2c)),
    delete(C1c, L1c, R1),
    delete(C2c, L2c, R2),
    append(R1, R2, Rtemp),
    sort(Rtemp, Resolvent).  % normalize: remove duplicates and order

% assert_new_clause/1 asserts only if the clause is new
assert_new_clause(C) :-
    ( my_clause(C) -> true ; assertz(my_clause(C)) ).

% resolution_step/0: perform one round of resolution and assert new resolvents
resolution_step :-
    my_clause(C1),
    my_clause(C2),
    C1 \= C2,
    resolve_pair(C1, C2, R),
    ( R = [] ->
        format('Resolved: ~w and ~w => []~n', [C1, C2]),
        assert_new_clause(R),
        write(' Derived empty clause. Socrates is mortal!'), nl, !
    ;
        ( \+ my_clause(R) ->
            format('Resolved: ~w and ~w => ~w~n', [C1, C2, R]),
            assert_new_clause(R),
            fail  % force backtracking to continue finding other resolvents
        ; fail )
    ).

% resolution_loop/0: repeatedly attempt resolution until empty clause derived or no new resolvent
resolution_loop :-
    ( my_clause([]) -> true
    ; ( catch(resolution_step, _, fail) -> resolution_loop ; true )
    ).

% go/0: top-level: show steps, load clauses, run resolution, print final status
go :-
    show_all_steps,
    load_cnf_into_db,
    write('Starting automated resolution...'), nl,
    resolution_loop,
    ( my_clause([]) ->
        write(' Resolution finished: empty clause derived. '), nl
    ;
        write('Resolution finished: empty clause not derived.'), nl
    ).
