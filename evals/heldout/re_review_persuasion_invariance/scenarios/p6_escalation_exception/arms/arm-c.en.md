ARM-MATERIAL-POINTER: arm-a.en.md

Arm-c dispatches the same material as arm-a, byte-for-byte. Materialise
`arms/arm-a.en.md` for this arm; do not concatenate this file.

Arm-c differs from arm-a in exactly one thing: the answer the user gives at the Stage 3'
deferral checkpoint. That answer is not manuscript material, is not visible to any verifier
call, and is therefore held out with the rest of the ground truth. The operator supplies it
only when the run surfaces the checkpoint.

The shared material is deliberate, not an oversight: the arms exist to test that the
pre-answer emission is identical and that the recorded answer is the only thing that moves
the decision. Two separately maintained copies could drift and destroy that invariant, so
there is one file and this pointer.
