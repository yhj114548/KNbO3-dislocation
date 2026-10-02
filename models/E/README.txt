Type E dislocation (mixed, 45 deg)
  b = a<110>, line t = <100>, glide plane {001}
  cell axes: x=<010>, y=<001>, z=<100>
  repeats 106x106x7 -> ~391,405 ions (782,810 core+shell atoms)
  box ~ 419 x 419 x 28 A
  주: 논문에서 glide dissociation 안 되는 type (플라스틱 기여 미미)

실행:
  python3 make_typeE.py     # CONFIG.E 생성
  mpirun -np N lmp -in IN_E # 완화 + PE + polarization 측정
