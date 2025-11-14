(define (problem cleaning_problem)
  (:domain cleaning)
  
  (:objects
    classroom cafeteria dustbin - location
  )
  
  (:init
    (at classroom)
    (dirty classroom)
    (dirty cafeteria)
    (has-trash classroom)
    (has-trash cafeteria)
    (adjacent classroom cafeteria)
    (adjacent cafeteria classroom)
    (adjacent cafeteria dustbin)
    (adjacent dustbin cafeteria)
  )
  
  (:goal
    (and
      (mopped classroom)
      (mopped cafeteria)
      (not (carrying-trash))
      (not (has-trash classroom))
      (not (has-trash cafeteria))
    )
  )
)