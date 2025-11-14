(define (domain cleaning)
  (:requirements :strips :typing)
  
  (:types location)
  
  (:predicates
    (at ?l - location)
    (dirty ?l - location)
    (swept ?l - location)
    (mopped ?l - location)
    (has-trash ?l - location)
    (carrying-trash)
    (adjacent ?l1 ?l2 - location)
  )
  
  (:action move
    :parameters (?from ?to - location)
    :precondition (and (at ?from) (adjacent ?from ?to))
    :effect (and (not (at ?from)) (at ?to))
  )
  
  (:action sweep
    :parameters (?l - location)
    :precondition (and (at ?l) (dirty ?l))
    :effect (and (not (dirty ?l)) (swept ?l))
  )
  
  (:action mop
    :parameters (?l - location)
    :precondition (and (at ?l) (swept ?l))
    :effect (and (not (swept ?l)) (mopped ?l))
  )
  
  (:action pick-trash
    :parameters (?l - location)
    :precondition (and (at ?l) (has-trash ?l) (not (carrying-trash)))
    :effect (and (not (has-trash ?l)) (carrying-trash))
  )
  
  (:action drop-trash
    :parameters ()
    :precondition (and (at dustbin) (carrying-trash))
    :effect (not (carrying-trash))
  )
)