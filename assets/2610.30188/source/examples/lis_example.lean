import Mathlib

namespace LISExample

def lisOriginal (nums : List Int) : Nat :=
  let max2 (a : Nat) (b : Nat) : Nat :=
    if a > b then a else b

  let rec helper (lst : List Int)
      (prev : Option Int) : Nat :=
    match lst with
    | [] => 0
    | h :: t =>
        let canTake : Bool :=
          if prev = none then true
          else if prev.get! < h then true
          else false
        let withTake : Nat :=
          if canTake then
            1 + helper t (some h)
          else 0
        let withoutTake := helper t prev
        max2 withTake withoutTake

  helper nums none

def lisTableQuery :
    List (Int × Nat) → Option Int → Nat
  | [], _ => 0
  | (value, len) :: entries, none =>
      Nat.max len
        (lisTableQuery entries none)
  | (value, len) :: entries, some prev =>
      if prev < value then
        Nat.max len
          (lisTableQuery entries (some prev))
      else
        lisTableQuery entries (some prev)

def lisTable : List Int → List (Int × Nat)
  | [] => []
  | value :: values =>
      let entries := lisTable values
      (value, 1 + lisTableQuery entries
        (some value)) :: entries

def lisOptimized (nums : List Int) : Nat :=
  lisTableQuery (lisTable nums) none

theorem lis_equiv (nums : List Int) : lisOptimized nums = lisOriginal nums := by
  unfold lisOptimized lisOriginal
  suffices h : ∀ prev, lisTableQuery (lisTable nums) prev =
      lisOriginal.helper (fun a b => if a > b then a else b) nums prev by
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
          simp only [lisTable, lisTableQuery, lisOriginal.helper]
          rw [ih (some x), ih none]
          exact max_eq _ _
      | some p =>
          simp only [lisTable, lisTableQuery, lisOriginal.helper, Option.some.injEq, reduceCtorEq, ↓reduceIte,
            Option.get!, Bool.if_true_right]
          by_cases hp : p < x
          · simp only [hp, ↓reduceIte, Bool.true_eq]
            rw [ih (some x), ih (some p)]
            exact max_eq _ _
          · simp only [hp, ↓reduceIte, Bool.false_eq]
            rw [ih (some p)]
            simp

#print axioms lis_equiv

end LISExample
