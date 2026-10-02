Type D KNbO3: corrected rerun inputs
======================================
먼저 CHANGELOG.md를 읽으세요. 원본 ZIP은 변경하지 않았습니다.
이 폴더의 기존 log/dump/relaxed/측정 파일은 모두 과거 결과입니다.
새 구조와 새 입력이 그 계산을 성공적으로 마쳤다는 뜻이 아닙니다.

권장 실행:
  python3 prepare_run.py
  위 명령이 표시한 새 runs/run_... 폴더로 이동합니다.
  기존 환경에 맞게 job.pbs로 제출하거나 다음처럼 실행합니다.
  mpirun -np N lmp -in IN_D -log log.corrected.lammps

prepare_run.py는 먼저 입력 전체를 검사하고 현재 입력만 복사합니다.
작업을 자동 제출하거나 LAMMPS를 실행하지 않습니다. N은 MPI process 수입니다.
사전 검사만 할 때: python3 verify_inputs.py
두 스크립트는 Python 표준 라이브러리만 필요합니다.

CONFIG.D와 defect_group_D.txt가 이미 제공되므로 재생성은 필요하지 않습니다.
재생성하려면 numpy, scipy가 필요합니다:
  python3 make_typeD.py
  python3 check_coord.py
  python3 verify_inputs.py
제공된 fingerprint와 달라지면 새 원자 ID와 defect 선택을 다시 검증해야 합니다.
임의로 fingerprint만 갱신하여 불일치를 숨기지 마세요.

실행 후 확인:
  relaxation_D.status: STARTED -> STATIC_PASS -> MD_COMPLETE
  CONFIG.D_static: 모든 위치 구속을 없앤 정적 힘 검사 통과 시 생성
  CONFIG.D_relaxed: 전체 MD 완료 시 생성
  CONFIG.D_relax_failed / relaxation_D_failed.dump: 힘 기준 미달 시 기록
  실패하면 종료 코드 1로 중단하며 production MD로 넘어가지 않습니다.
  엔진 자체 오류가 먼저 생기면 실패 체크포인트를 못 남길 수도 있습니다.

잠재적 비물리 구조를 추가 repulsion으로 억지 안정화하지 않습니다.
미수렴이면 힘/에너지/짧은 거리 접촉과 초기 구조를 재검토해야 합니다.
LAMMPS 금속 단위 입력을 유지했으며, 분석 보고는 SI 단위입니다.
온도 30 K, 외부 압력 0 Pa, timestep 5e-16 s는 기존 설정입니다.
해당 timestep의 수렴과 adiabatic 안정성은 production 전에 확인해야 합니다.

검증 상세: VALIDATION.json, GEOMETRY_CHECKS.json, ENGINE_CHECKS.json
파일 변경 상세: CHANGES.patch, FILE_MANIFEST.json
논문 및 실행 검증의 한계: CHANGELOG.md
