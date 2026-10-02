# Type D 수정 기록

이 ZIP은 수정된 재실행 입력입니다. 새 production MD 결과가 아닙니다.

## D에서 확인한 문제와 구조 수정

| 원본 파일·행 | 확인 사항 | 수정 |
|---|---|---|
| CONFIG.D 17–18, IN_D 137–138 | K/Nb shell 질량 반전 및 두 shell을 같은 임의 질량으로 덮어쓰기 | 올바른 질량으로 재생성, mass override 제거 |
| IN_D 146–220 | WCA와 1–4/2–5/3–6 쌍의 추가 Buckingham repulsion | 원래 Param_KNO만 include |
| IN_D 289–339 | 구속 에너지 누락, 전하 ramp, 명시적 힘 수렴 기준 없는 최소화 | 단계적 구속 해제와 최종 힘 검사 |
| make_typeD.py 19–20 | edge Burgers vector가 x인데 삭제 ribbon 두께는 y; 원래 축은 왼손 좌표계 | x/y 교환으로 오른손 좌표계와 b_edge∥y 정렬 |
| check_coord.py 및 defect_group_D.txt | 기존 ID에 묶인 선택 | 새 좌표·ID에서 같은 coordination 기준으로 재생성 |

수정한 축은 x=[1,-1,-2], y=[1,1,0], z=[1,-1,1]입니다. 물리적 Burgers vector a[1,1,0]와 전위선 [1,-1,1]은 유지합니다. 이는 논문 Type D와 입방정 대칭으로 동등한 방향이며, 논문 Sec.2.2처럼 edge 성분이 y와 평행해집니다.[1]

반복 수 (66,66,3)는 유지하되 x/y 길이와 제거되는 층이 달라져 **389,070이온 / 778,140입자**가 됩니다. 원본은 390,060이온 / 780,120입자였습니다. 새 결함 선택은 같은 2.85×10⁻¹⁰ m cutoff와 종별 최빈 coordination 기준으로 2,869이온 / 5,738입자를 포함합니다. 기존 화학양론 보정 삭제는 유지했으며 oxygen-transfer에 의한 국소 charge balance를 새로 만든 것은 아닙니다.

D의 settle 5 K, 20,000 step=1×10⁻¹¹ s, dump 간격 100 step, NPT 압력 damping 1×10⁻¹¹ s, drag=2, nreset=1000, flip=no는 보존했습니다. 준비 단계의 속도 제한과 두 번의 정적 box-relax는 제거하고, 이후 원래 NPT에서 셀을 완화합니다.

원본 작업 출력에는 NPT step 2에서 Nb core–shell 한 쌍과 O 두 쌍의 missing-bond 오류가 있습니다. 앞선 최소화도 line-search 종료였으므로, 로그만으로 단일한 미시적 원인을 확정할 수 없습니다. 수정본의 실제 완화 성공 여부는 별도 확인이 필요합니다.

## 공통 수정

- 질량: type 4=K shell, type 5=Nb shell로 교정했습니다. 각각 약 5.90222×10⁻²⁷ kg, 1.40249×10⁻²⁶ kg이며 shell/core 질량비는 0.1입니다.[2] `CONFIG.IN`은 원래 올바르므로 그대로 사용했습니다. 생성 코드에는 질량비 오류를 중단시키는 검사를 추가했습니다.
- Potential: 임의의 추가 반발항을 제거하고 원본 `Param_KNO`만 사용합니다. 그 파일의 모든 계수, PPPM 정확도와 cutoff는 보존했습니다.[3]
- 준비: 전하 ramp, 느슨한 힘 통과 기준, 속도 제한 적분과 기존 정적 box-relax 단계를 제거했습니다. 고정 셀에서 core 고정/shell 최소화 → defect core 위치 구속을 단계적으로 해제 → 무구속 힘 검사 → 기존 저온 NPT에서 셀 완화 순서입니다.[1] Shell에는 별도 위치 스프링을 걸지 않습니다.
- 구속 에너지를 최소화 목적함수에 포함하고, 같은 기준 위치에 대한 강도를 240.3264951 → 80.1088317 → 16.02176634 → 1.602176634 → 0 N/m로 낮춥니다. 중간 허용 최대 원자 힘은 1.602176634×10⁻¹² N, 최종 무구속 허용값은 1.602176634×10⁻¹³ N입니다. `min_modify norm max`를 사용하므로 global two-norm과 다릅니다.
- 어느 단계에서든 힘 기준에 미달하면 실패 상태, 데이터와 힘 dump를 저장하고 종료 코드 1로 중단합니다. MD로 억지로 넘어가지 않습니다. 엔진 오류가 먼저 발생하면 체크포인트가 기록되기 전에 중단할 수도 있습니다.
- 첫 속도 초기화는 core–shell 질량중심 기준이며, NPT로 전환할 때는 `velocity ... scale ... bias yes temp Tcs`만 사용합니다. 상대 core–shell 속도를 새로 생성하거나 함께 스케일하지 않습니다. 내부 운동에너지를 J로 출력합니다.
- 원자 손실은 오류로 처리합니다. 절대 dipole/volume은 기존 진단량으로 유지하되 검증된 자발분극으로 해석하지 않습니다.[2] `pe_per_atom` 분모는 core+shell 입자 수이며 물리적 이온 수가 아닙니다.

위 구속 강도·힘 기준·최소화 횟수는 **이번에 제안한 준비 절차**입니다. Klomp 논문은 단계적 구속 해제 원칙만 제시하므로 이 수치들을 논문에 명시된 protocol이라고 볼 수 없습니다. 원래 전하와 potential에서 수렴·adiabatic 안정성·core 구조가 확인되어야 합니다.

## 유지한 설정과 보존한 기록

기존 폴더명과 파일 위치를 보존했습니다. 원본 ZIP은 수정하지 않았습니다. `Param_KNO`, `CONFIG.IN`, `job.pbs`는 바이트 단위로 유지했습니다. 생산 온도 30 K, 외부 압력 0 Pa, 시간 간격 5×10⁻¹⁶ s, NPT 평형화 1×10⁻¹⁰ s 및 측정 5×10⁻¹¹ s를 유지했습니다. 원자 구조는 아래의 생성 오류 때문에 재생성했으므로 기존 좌표·ID를 보존한 수정은 아닙니다.

기존 `log.lammps`, 배치 작업 출력, 에너지·분극 파일, dump와 relaxed 구조가 있다면 모두 **과거 입력으로 계산한 기록**입니다. 새 입력의 결과로 해석하면 안 됩니다. `prepare_run.py`는 정합성을 검사하고 현재 입력만 새 `runs/` 폴더에 복사합니다. 기존 `job.pbs`를 그 새 폴더에서 사용하면 과거 결과와 섞이지 않습니다.

새 구조가 원래 전위를 물리적으로 재현했다고 확정하려면, 실제 수렴 후 Burgers circuit/disregistry, 국소 전하, partial 분리, 내부 운동에너지의 시간 추이와 시간 간격/크기/초기 속도 민감도를 확인해야 합니다. 총 전하 0 C는 각 core의 국소 중성을 뜻하지 않습니다.[1] SrTiO₃ 결과를 KNbO₃에 그대로 강제해서는 안 됩니다.

## 논문과 구현 근거

1. Klomp, Porz & Albe, *The nature and motion of deformation-induced dislocations in SrTiO₃: Insights from atomistic simulations*, Acta Materialia 242 (2023) 118404. Table 1, Sec.2.2, Type B/D 절. [DOI](https://doi.org/10.1016/j.actamat.2022.118404). 논문 대상은 SrTiO₃이며 KNbO₃의 같은 분리거리·이동응력을 보증하지 않습니다.
2. Khadka & Keblinski, *Molecular dynamics study of domain switching dynamics in KNbO₃ and BaTiO₃*, J. Mater. Sci. 57 (2022) 12929–12946, p.12931. [DOI](https://doi.org/10.1007/s10853-022-07407-1). KNbO₃의 shell/core 질량비 0.1 및 기준 구조 대비 변위에 근거한 분극 계산의 근거입니다.
3. Sepliarsky et al., *Atomic-level simulation of ferroelectricity in oxide materials*, Current Opinion in Solid State & Materials Science 9 (2005) 107–113, p.109 Table 1 및 spring 식. [DOI](https://doi.org/10.1016/j.cossms.2006.05.002). 주어진 전하·Buckingham·core–shell 계수의 근거입니다. 논문 k₂/2 및 k₄/24가 LAMMPS class2 계수에 대응하므로 Param_KNO는 유지했습니다.
4. Cai et al., *Periodic image effects in dislocation modelling*, Philosophical Magazine 83 (2003) 539–567, Sec.4.1, Eqs.20–22. [저자 제공 논문](https://micro.stanford.edu/~caiwei/papers/Cai03pm-image.pdf), [DOI](https://doi.org/10.1080/0141861021000051109). Screw dipole 변위장의 주기 경계 정합성과 비주기적 선형항 보정의 근거입니다. 이 ZIP의 theta-function 표현 자체를 해당 논문이 제시한 식이라고 주장하지 않습니다.

소프트웨어 명령은 논문과 구분하여 LAMMPS [core/shell](https://docs.lammps.org/stable/Howto_coreshell.html), [spring/self](https://docs.lammps.org/stable/fix_spring_self.html), [min_modify](https://docs.lammps.org/stable/min_modify.html), [velocity](https://docs.lammps.org/stable/velocity.html)를 참조했습니다. 실행 검증 버전은 LAMMPS 22 Jul 2025 Update 4입니다.

## 실제 검증 범위

- 생성 데이터 전수 검사: 778,140입자의 종별 질량·전하, 일대일 core–shell 결합과 분자 ID, 화학양론 및 defect 선택의 일관성을 확인했습니다.
- 전체 데이터 LAMMPS 초기 힘 평가: 정상 종료, initial PE -1.9667989e-12 J, 최대 원자 힘 1.3337181e-07 N. 초기 힘은 최종 수렴 기준보다 큽니다.
- 축소한 10입자 fixture에서 여섯 구속/힘 검사 단계, 짧은 NVE/NPT와 출력 명령이 실행됐습니다. 별도 실패 시험은 상태 1로 중단하고 실패 구조와 힘 dump를 기록했습니다.
- 축소 fixture에서만 force tolerance를 1.602176634e-10 N로 완화하고 settle/NPT/production을 각각 2 step으로 줄였습니다. 배포 입력에는 원래 계획한 엄격한 힘 기준과 전체 길이가 남아 있습니다.
- **전체 구조의 정적 수렴, 장시간 MD, 시간 간격 수렴, partial 분리 및 국소 전하 검증은 수행하지 않았습니다.** run 0의 정상 종료는 이 항목들의 성공을 뜻하지 않습니다.

확인 가능한 수치와 실행 버전은 ENGINE_CHECKS.json, 초기 엔진 로그는 validation_run0.log에 있습니다.

참고: 같은 실행기 시험에서 이전 C 수정본의 NPT 전환 속도 처리를 교정했습니다. 별도 C_corrected_v2.zip과 전체 검토 요약을 참조하세요.
