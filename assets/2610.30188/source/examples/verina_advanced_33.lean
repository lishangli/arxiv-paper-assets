import Mathlib

-- !benchmark @start import type=solution
import Mathlib.Data.List.Basic
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux
@[reducible, simp]
def longestIncreasingSubsequence_precond (nums : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def longestIncreasingSubsequence (nums : List Int) (h_precond : longestIncreasingSubsequence_precond (nums)) : Nat :=
  -- !benchmark @start code
  let max2 (a : Nat) (b : Nat) : Nat :=
    if a > b then a else b

  let rec listLength (l : List Int) : Nat :=
    match l with
    | []      => 0
    | _ :: xs => 1 + listLength xs

  let rec helper (lst : List Int) (prev : Option Int) : Nat :=
    match lst with
    | [] => 0
    | h :: t =>
        let canTake : Bool :=
          if prev = none then true
          else if prev.get! < h then true else false
        let withTake : Nat :=
          if canTake then 1 + helper t (some h) else 0
        let withoutTake : Nat := helper t prev
        max2 withTake withoutTake

  let result := helper nums none
  result
  -- !benchmark @end code

-- Candidate artifact
def lisTableQuery : List (Int × Nat) → Option Int → Nat
  | [], _ => 0
  | (value, len) :: entries, none =>
      Nat.max len (lisTableQuery entries none)
  | (value, len) :: entries, some prev =>
      if prev < value then
        Nat.max len (lisTableQuery entries (some prev))
      else
        lisTableQuery entries (some prev)

def lisTable : List Int → List (Int × Nat)
  | [] => []
  | value :: values =>
      let entries := lisTable values
      (value, 1 + lisTableQuery entries (some value)) :: entries

def longestIncreasingSubsequence_optimized (nums : List Int) (h_precond : longestIncreasingSubsequence_precond nums) : Nat :=
  lisTableQuery (lisTable nums) none

theorem longestIncreasingSubsequence_optimized_eq_baseline (nums : List Int) (h_precond : longestIncreasingSubsequence_precond nums) :
    longestIncreasingSubsequence_optimized nums h_precond = longestIncreasingSubsequence nums h_precond := by
  unfold longestIncreasingSubsequence_optimized longestIncreasingSubsequence
  clear h_precond
  suffices h : ∀ prev, lisTableQuery (lisTable nums) prev =
      longestIncreasingSubsequence.helper (fun a b => if a > b then a else b) nums prev by
    exact h none
  have max_eq (a b : Nat) : Nat.max a b = (if a > b then a else b) := by
    rw [Nat.max_eq_max]
    by_cases hab : a > b
    · rw [if_pos hab, Nat.max_eq_left (Nat.le_of_lt hab)]
    · rw [if_neg hab, Nat.max_eq_right (Nat.le_of_not_gt hab)]
  induction nums with
  | nil => intro prev; rfl
  | cons x xs ih =>
      intro prev
      cases prev with
      | none =>
          simp only [lisTable, lisTableQuery, longestIncreasingSubsequence.helper]
          rw [ih (some x), ih none]
          exact max_eq _ _
      | some p =>
          simp only [lisTable, lisTableQuery, longestIncreasingSubsequence.helper, Option.some.injEq, reduceCtorEq, ↓reduceIte,
            Option.get!, Bool.if_true_right]
          by_cases hp : p < x
          · simp only [hp, ↓reduceIte, Bool.true_eq]
            rw [ih (some x), ih (some p)]
            exact max_eq _ _
          · simp only [hp, ↓reduceIte, Bool.false_eq]
            rw [ih (some p)]
            simp

-- Machine-generated protocol conformance checks
example (nums : List Int) (h_precond : longestIncreasingSubsequence_precond nums) : Nat :=
  longestIncreasingSubsequence_optimized nums h_precond

example (nums : List Int) (h_precond : longestIncreasingSubsequence_precond nums) :
    longestIncreasingSubsequence_optimized nums h_precond = longestIncreasingSubsequence nums h_precond :=
  longestIncreasingSubsequence_optimized_eq_baseline nums h_precond

#print axioms longestIncreasingSubsequence_optimized_eq_baseline
