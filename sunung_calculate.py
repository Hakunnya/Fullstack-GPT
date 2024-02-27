import pandas as pd
import numpy as np

the_path = "./files/sunung_total_score2023.xlsx"
db_origin = pd.read_excel(the_path, 'DB')
score_dup = pd.read_excel(the_path, '원표백등')
trance_score = pd.read_excel(the_path, 'trance_tamscore')
trance_index = pd.read_excel(the_path, 'trance_index', usecols = ['school_code', 'DB_tra_code', 'tra_type'])
user = pd.read_excel(the_path, 'user_score')
#same_score = pd.read_excel(the_path, '동점자', usecols = ['계열', '수능활용점수', '동점자조합', '조합점수', '동점자_국', '동점자_수', '동점자_탐1', '동점자_탐2'])
stock = pd.read_excel(the_path, '상위누적')
johab_name = pd.read_excel(the_path, '조합명')
db_part1 = db_origin.loc[:, '대학명':'탐구등급점수9등급']
db_part2 = db_origin.loc[:, '동점자_영어':'소신누적(최종컷)']
db_part3 = pd.concat([db_part1, db_part2], axis=1)

johab_name['지원조합번호'] = johab_name['지원조합번호'].fillna(0)
johab_name['지원조합번호'] = johab_name['지원조합번호'].astype(np.int64)
johab_name_single_dup = johab_name[['수능조합', '탐구개수', '지원조합번호', '산출번호']]
johab_name_single = johab_name_single_dup.drop_duplicates(['수능조합'])
score = score_dup.drop_duplicates(['과목코드', '표점'])

# ===========================가이드컷 <-> 환산점수 교체 영역 시작=================================
#common002 계산용 점수 부여
def func_common(score_card):
    df = pd.merge(db_part3, johab_name_single, how='left', on='수능조합')
    # common001 별도산출 및 변표를 위해 모집단위 코드에서 대학코드 생성
    df['대학코드'] = df['모집요강코드'].apply(str).str[:5]
    df['대학코드'] = pd.to_numeric(df['대학코드'])

    # psc: 응시자 표준점수, bsc; 응시자 백분위, dsc: 응시자 등급
    df['유저명'] = str(score_card[0])
    kor_dsc = int(score_card[1])
    guk_psc = int(score_card[2])
    guk_bsc = int(score_card[3])
    guk_dsc = int(score_card[4])
    su_select = str(score_card[5])
    su_psc = int(score_card[6])
    su_bsc = int(score_card[7])
    su_dsc = int(score_card[8])
    eng_dsc = int(score_card[9])
    tam1_select = str(score_card[10])
    tam1_psc = int(score_card[11])
    tam1_bsc = int(score_card[12])
    tam1_dsc = int(score_card[13])
    tam2_select = str(score_card[14])
    tam2_psc = int(score_card[15])
    tam2_bsc = int(score_card[16])
    tam2_dsc = int(score_card[17])
    # user.loc[user['제2외선택'] == '한문', '제2외선택'] = '중국어' #중국어 관련학과에 중국어 or 한문에 가산점을 주거나 대체 하는 케이스를 위해 만듬(매년 확인 필요)
    foreign_select = str(score_card[18])
    foreign_dsc = int(score_card[19])
    df['tam1_select'] = tam1_select
    df['tam2_select'] = tam2_select

    #common003 과목별 표준점수 최고점
    top_scr_guk = score['표점'].loc[(score['과목명'] == '국어')].max()
    top_scr_su = score['표점'].loc[(score['과목명'] == '수학')].max()
    top_scr_tam1 = score['표점'].loc[(score['과목명'] == tam1_select)].max()
    top_scr_tam2 = score['표점'].loc[(score['과목명'] == tam2_select)].max()

    #common004 한국사, 영어, 제2외 등급점수
    df_eng = df.loc[:, '영어적용기준':'영어9등급점수']
    df_kor = df.loc[:, '한국사적용기준':'한국사9등급점수']
    df_foreign = df.loc[:, '제2외/한적용기준':'제2외/한9등급점수']
    df['영어'] = df_eng.iloc[:, eng_dsc]
    df['한국사'] = df_kor.iloc[:, kor_dsc]
    if foreign_dsc == 0:
        df['제2외'] = 0
    else:
        df['제2외'] = df_foreign.iloc[:, foreign_dsc + 1]
    df.loc[(df['제2외/한과목선택'] != '제2외전체') & (df['제2외/한과목선택'].apply(str).str[:1] != foreign_select[:1]), '제2외'] = 0

    #common005 영어, 한국사, 제2외 환산점수 완료
    df.loc[(df['한국사적용기준'] == '가산점') | (df['한국사적용기준'] == '수능비율포함'), '한국사환산점수'] = df['한국사']
    df.loc[(df['한국사적용기준'] != '가산점') & (df['한국사적용기준'] != '수능비율포함') & (df['한국사적용기준'] != '별도산출'), '한국사환산점수'] = 0
    df.loc[(df['제2외/한적용기준'] == '가산점') | (df['제2외/한적용기준'] == '수능비율포함'), '제2외환산점수'] = df['제2외']
    df.loc[(df['제2외/한적용기준'] != '가산점') & (df['제2외/한적용기준'] != '수능비율포함'), '제2외환산점수'] = 0
    df.loc[(df['영어적용기준'] == '가산점') | (df['영어적용기준'] == '수능비율포함'), '영어환산점수'] = df['영어']
    df.loc[(df['영어적용기준'] != '가산점') & (df['영어적용기준'] != '수능비율포함'), '영어환산점수'] = 0

    #common006 영역별 원점 생성 (표준점수, 백분위)
    df.loc[(df['국어활용기준'] == '표준점수') | (df['국어활용기준'] == '표준최고환산'), '국어원점'] = guk_psc
    df.loc[(df['수학활용기준'] == '표준점수') | (df['국어활용기준'] == '표준최고환산'), '수학원점'] = su_psc
    df.loc[(df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산'), '탐1원점'] = tam1_psc
    df.loc[(df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산'), '탐2원점'] = tam2_psc
    df.loc[((df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산')) & (df['탐구개수'] == 2), '탐평원점'] = tam1_psc + tam2_psc
    df.loc[((df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산')) & (df['탐구개수'] == 1), '탐평원점'] = 2 * max(tam1_psc, tam2_psc)
    df.loc[df['국어활용기준'] == '백분위', '국어원점'] = guk_bsc
    df.loc[df['수학활용기준'] == '백분위', '수학원점'] = su_bsc
    df.loc[(df['탐구활용기준'] == '백분위') | (df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '변표최고환산'), '탐1원점'] = tam1_bsc
    df.loc[(df['탐구활용기준'] == '백분위') | (df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '변표최고환산'), '탐2원점'] = tam2_bsc
    df.loc[(df['탐구활용기준'] == '백분위') | (df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '변표최고환산') & (df['탐구개수'] == 2), '탐평원점'] = (tam1_bsc + tam2_bsc) / 2
    df.loc[(df['탐구활용기준'] == '백분위') | (df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '변표최고환산'), '탐평원점'] = max(tam1_bsc, tam2_bsc)

    #common007 수학 가산점 부여 여부 체크
    su_extra = su_select+'가산점'

    #common008 탐구 가산점 부여 여부 체크
    if tam1_select == '물리학1' or tam1_select == '화학1' or tam1_select == '생명과학1' or tam1_select == '지구과학1' or tam1_select == '물리학2' or tam1_select == '화학2' or tam1_select == '생명과학2' or tam1_select == '지구과학2':
        tam1_extra00 = '과학가산점'
    else:
        tam1_extra00 = '사회가산점'
    if tam2_select == '물리학1' or tam2_select == '화학1' or tam2_select == '생명과학1' or tam2_select == '지구과학1' or tam2_select == '물리학2' or tam2_select == '화학2' or tam2_select == '생명과학2' or tam2_select == '지구과학2':
        tam2_extra00 = '과학가산점'
    else:
        tam2_extra00 = '사회가산점'

    #common009 탐구 가산 과목이 특정된 경우 : 매년 요강 변경시 확인 필요 - 하드코딩
    # 물리학II,화학II,생명과학II,지구과학II - 01
    if tam1_select == '물리학2' or tam1_select == '화학2' or tam1_select == '생명과학2' or tam1_select == '지구과학2':
        tam1_extra01 = '과학가산점'
    else:
        tam1_extra01 = '사회가산점'
    if tam2_select == '물리학2' or tam2_select == '화학2' or tam2_select == '생명과학2' or tam2_select == '지구과학2':
        tam2_extra01 = '과학가산점'
    else:
        tam2_extra01 = '사회가산점'

    # 물리학II,화학II,생명과학II - 02
    if tam1_select == '물리학2' or tam1_select == '화학2' or tam1_select == '생명과학2':
        tam1_extra02 = '과학가산점'
    else:
        tam1_extra02 = '사회가산점'
    if tam2_select == '물리학2' or tam2_select == '화학2' or tam2_select == '생명과학2':
        tam2_extra02 = '과학가산점'
    else:
        tam2_extra02 = '사회가산점'

    # 물리학I,물리학II - 03
    if tam1_select == '물리학1' or tam1_select == '물리학2':
        tam1_extra03 = '과학가산점'
    else:
        tam1_extra03 = '사회가산점'
    if tam2_select == '물리학1' or tam2_select == '물리학2':
        tam2_extra03 = '과학가산점'
    else:
        tam2_extra03 = '사회가산점'

    # 생명과학I,생명과학II - 04
    if tam1_select == '생명과학1' or tam1_select == '생명과학2':
        tam1_extra04 = '과학가산점'
    else:
        tam1_extra04 = '사회가산점'
    if tam2_select == '생명과학1' or tam2_select == '생명과학2':
        tam2_extra04 = '과학가산점'
    else:
        tam2_extra04 = '사회가산점'

    # 지구과학I,지구과학II - 05
    if tam1_select == '지구과학1' or tam1_select == '지구과학2':
        tam1_extra05 = '과학가산점'
    else:
        tam1_extra05 = '사회가산점'
    if tam2_select == '지구과학1' or tam2_select == '지구과학2':
        tam2_extra05 = '과학가산점'
    else:
        tam2_extra05 = '사회가산점'

    # 화학I,화학II - 06
    if tam1_select == '화학1' or tam1_select == '화학2':
        tam1_extra06 = '과학가산점'
    else:
        tam1_extra06 = '사회가산점'
    if tam2_select == '화학1' or tam2_select == '화학2':
        tam2_extra06 = '과학가산점'
    else:
        tam2_extra06 = '사회가산점'

    # 화학II,생명과학II - 07
    if tam1_select == '화학2' or tam1_select == '생명과학2':
        tam1_extra07 = '과학가산점'
    else:
        tam1_extra07 = '사회가산점'
    if tam2_select == '화학2' or tam2_select == '생명과학2':
        tam2_extra07 = '과학가산점'
    else:
        tam2_extra07 = '사회가산점'

    # 생활과윤리,윤리와사상 - 08
    if tam1_select == '생활과윤리' or tam1_select == '윤리와사상':
        tam1_extra08 = '사회가산점'
    else:
        tam1_extra08 = '과학가산점'
    if tam2_select == '생활과윤리' or tam2_select == '윤리와사상':
        tam2_extra08 = '사회가산점'
    else:
        tam2_extra08 = '과학가산점'

    #common010 탐구 가산 과목이 특정된 경우 : 매년 요강 변경시 확인 필요 - 하드코딩
    tam_name_extra00 = '과탐'
    tam_name_extra01 = '물리학II,화학II,생명과학II,지구과학II'
    tam_name_extra02 = '물리학II,화학II,생명과학II'
    tam_name_extra03 = '물리학I,물리학II'
    tam_name_extra04 = '생명과학I,생명과학II'
    tam_name_extra05 = '지구과학I,지구과학II'
    tam_name_extra06 = '화학I,화학II'
    tam_name_extra07 = '화학II,생명과학II'
    tam_name_extra08 = '생활과윤리,윤리와사상'
    list_tam_extras = [tam_name_extra00, tam_name_extra01, tam_name_extra02, tam_name_extra03, tam_name_extra04, tam_name_extra05, tam_name_extra06, tam_name_extra07, tam_name_extra08]
    list_tam_ex_result1 = [tam1_extra00, tam1_extra01, tam1_extra02, tam1_extra03, tam1_extra04, tam1_extra05, tam1_extra06, tam1_extra07, tam1_extra08]
    list_tam_ex_result2 = [tam2_extra00, tam2_extra01, tam2_extra02, tam2_extra03, tam2_extra04, tam2_extra05, tam2_extra06, tam2_extra07, tam2_extra08]

    # common011 변환표준점수 반영
    # A타입: 응시자가 사탐응시 했는가 과탐응시 했는가에 따라 부여
    # B타입: 모집단위 분류가 인문인가 자연인가에 따라 부여(변표코드에 따라 다르게 부여)
    # C타입: 중앙대 예외케이스
    list_A_type = list(trance_index['school_code'].loc[trance_index['tra_type'] == 'A'])
    list_B_type_school = list(trance_index['school_code'].loc[trance_index['tra_type'] == 'B'])
    list_B_type_dbcode = list(trance_index['DB_tra_code'].loc[trance_index['tra_type'] == 'B'])
    list_C_type_school = list(trance_index['school_code'].loc[trance_index['tra_type'] == 'C'])
    list_C_type_dbcode = list(trance_index['DB_tra_code'].loc[trance_index['tra_type'] == 'C'])

    # 유저 응시 탐구 과목에 따른 사과탐 분류
    if tam1_select == '물리학1' or tam1_select == '화학1' or tam1_select == '생명과학1' or tam1_select == '지구과학1' or tam1_select == '물리학2' or tam1_select == '화학2' or tam1_select == '생명과학2' or tam1_select == '지구과학2':
        user_tam1_type = '과탐'
    else:
        user_tam1_type = '사탐'
    if tam2_select == '물리학1' or tam2_select == '화학1' or tam2_select == '생명과학1' or tam2_select == '지구과학1' or tam2_select == '물리학2' or tam2_select == '화학2' or tam2_select == '생명과학2' or tam2_select == '지구과학2':
        user_tam2_type = '과탐'
    else:
        user_tam2_type = '사탐'

    # A타입 변표 값 테이블 생성
    df_tam_traA = pd.DataFrame(
        columns=['school_code_tra', 'DB_tra_code', 'tam1_tra', 'tam2_tra', 'tam1_tr_top', 'tam2_tr_top'])
    for school in list_A_type:
        tam1_traA_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "A") & (trance_score['구분'] == user_tam1_type) & (
                        trance_score['종료값'] == tam1_bsc) & (trance_score['학교코드'] == school)]
        tam2_traA_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "A") & (trance_score['구분'] == user_tam2_type) & (
                        trance_score['종료값'] == tam2_bsc) & (trance_score['학교코드'] == school)]
        tam1_trA_top_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "A") & (trance_score['구분'] == user_tam1_type) & (trance_score['종료값'] == 100) & (
                        trance_score['학교코드'] == school)]
        tam2_trA_top_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "A") & (trance_score['구분'] == user_tam2_type) & (trance_score['종료값'] == 100) & (
                        trance_score['학교코드'] == school)]
        tam1_traA = tam1_traA_as.iloc[0]
        tam2_traA = tam2_traA_as.iloc[0]
        tam1_trA_top = tam1_trA_top_as.iloc[0]
        tam2_trA_top = tam2_trA_top_as.iloc[0]
        df_tam_traA_as = pd.DataFrame([[school, 1, tam1_traA, tam2_traA, tam1_trA_top, tam2_trA_top]],
                                      columns=['school_code_tra', 'DB_tra_code', 'tam1_tra', 'tam2_tra', 'tam1_tr_top',
                                               'tam2_tr_top'])
        df_tam_traA = pd.concat([df_tam_traA, df_tam_traA_as], axis=0)
    df_tam_traA = df_tam_traA.drop_duplicates(['school_code_tra'], keep='first', ignore_index=True)  # 대학 중복 제거

    # B타입 변표 값 테이블 생성
    df_tam_traB = pd.DataFrame(
        columns=['school_code_tra', 'DB_tra_code', 'tam1_tra', 'tam2_tra', 'tam1_tr_top', 'tam2_tr_top'])
    for school, tra_code in zip(list_B_type_school, list_B_type_dbcode):
        tam1_traB_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "B") & (trance_score['요강DB변표코드'] == tra_code) & (
                        trance_score['종료값'] == tam1_bsc) & (trance_score['학교코드'] == school)]
        tam1_traB = tam1_traB_as.iloc[0]
        tam2_traB_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "B") & (trance_score['요강DB변표코드'] == tra_code) & (
                        trance_score['종료값'] == tam2_bsc) & (trance_score['학교코드'] == school)]
        tam2_traB = tam2_traB_as.iloc[0]
        tam1_trB_top_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "B") & (trance_score['요강DB변표코드'] == tra_code) & (trance_score['종료값'] == 100) & (
                        trance_score['학교코드'] == school)]
        tam1_trB_top = tam1_trB_top_as.iloc[0]
        tam2_trB_top_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == "B") & (trance_score['요강DB변표코드'] == tra_code) & (trance_score['종료값'] == 100) & (
                        trance_score['학교코드'] == school)]
        tam2_trB_top = tam2_trB_top_as.iloc[0]
        df_tam_traB_as = pd.DataFrame([[school, tra_code, tam1_traB, tam2_traB, tam1_trB_top, tam2_trB_top]],
                                      columns=['school_code_tra', 'DB_tra_code', 'tam1_tra', 'tam2_tra', 'tam1_tr_top',
                                               'tam2_tr_top'])
        df_tam_traB = pd.concat([df_tam_traB, df_tam_traB_as], axis=0, ignore_index=True)

    # C타입 변표 값 테이블 생성 (중앙대 only)
    df_tam_traC = pd.DataFrame(
        columns=['school_code_tra', 'DB_tra_code', 'tam1_tra', 'tam2_tra', 'tam1_tr_top', 'tam2_tr_top'])
    for school, tra_code in zip(list_C_type_school, list_C_type_dbcode):
        tam1_traC_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == 'C') & (trance_score['요강DB변표코드'] == tra_code) & (
                        trance_score['구분'] == user_tam1_type) & (trance_score['종료값'] == tam1_bsc) & (
                        trance_score['학교코드'] == school)]
        tam2_traC_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == 'C') & (trance_score['요강DB변표코드'] == tra_code) & (
                        trance_score['구분'] == user_tam2_type) & (trance_score['종료값'] == tam2_bsc) & (
                        trance_score['학교코드'] == school)]
        tam1_trC_top_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == 'C') & (trance_score['요강DB변표코드'] == tra_code) & (
                        trance_score['구분'] == user_tam1_type) & (trance_score['종료값'] == 100) & (
                        trance_score['학교코드'] == school)]
        tam2_trC_top_as = trance_score['변표환산값'].loc[
            (trance_score['변표type'] == 'C') & (trance_score['요강DB변표코드'] == tra_code) & (
                        trance_score['구분'] == user_tam2_type) & (trance_score['종료값'] == 100) & (
                        trance_score['학교코드'] == school)]
        tam1_traC = tam1_traC_as.iloc[0]
        tam2_traC = tam2_traC_as.iloc[0]
        tam1_trC_top = tam1_trC_top_as.iloc[0]
        tam2_trC_top = tam2_trC_top_as.iloc[0]
        df_tam_traC_as1 = pd.DataFrame([[school, tra_code, tam1_traC, tam2_traC, tam1_trC_top, tam2_trC_top]],
                                       columns=['school_code_tra', 'DB_tra_code', 'tam1_tra', 'tam2_tra', 'tam1_tr_top', 'tam2_tr_top'])
        df_tam_traC_as3 = pd.DataFrame([[school, tra_code, tam1_traC, tam2_traC, tam1_trC_top, tam2_trC_top]],
                                       columns=['school_code_tra', 'DB_tra_code', 'tam1_tra', 'tam2_tra', 'tam1_tr_top', 'tam2_tr_top'])
        df_tam_traC = pd.concat([df_tam_traC, df_tam_traC_as1, df_tam_traC_as3], axis=0)
    df_tam_traC = df_tam_traC.drop_duplicates(['school_code_tra', 'DB_tra_code'], keep='first', ignore_index=True)  # 대학 중복 제거
    df_tam_trance = pd.concat([df_tam_traA, df_tam_traB, df_tam_traC], axis=0, ignore_index=True)

    # df에 학과별 변표 적용 컬럼 신규 생성
    for tr_school_cd, tr_cd, tra1 in zip(df_tam_trance['school_code_tra'], df_tam_trance['DB_tra_code'], df_tam_trance['tam1_tra']):
        df.loc[(df['대학코드'] == tr_school_cd) & (df['변환표준공식번호'] == tr_cd), '탐1원점'] = tra1
    for tr_school_cd, tr_cd, tra2 in zip(df_tam_trance['school_code_tra'], df_tam_trance['DB_tra_code'], df_tam_trance['tam2_tra']):
        df.loc[(df['대학코드'] == tr_school_cd) & (df['변환표준공식번호'] == tr_cd), '탐2원점'] = tra2

    # 변표 최고점 컬럼 생성
    df.loc[df['변환표준공식번호'].isnull(), '탐1표점최고'] = top_scr_tam1
    for tr_school_cd, tr_cd, tr1_top in zip(df_tam_trance['school_code_tra'], df_tam_trance['DB_tra_code'], df_tam_trance['tam1_tr_top']):
        df.loc[(df['대학코드'] == tr_school_cd) & (df['변환표준공식번호'] == tr_cd), '탐1표점최고'] = tr1_top
    df.loc[df['변환표준공식번호'].isnull(), '탐2표점최고'] = top_scr_tam2
    for tr_school_cd, tr_cd, tr2_top in zip(df_tam_trance['school_code_tra'], df_tam_trance['DB_tra_code'], df_tam_trance['tam2_tr_top']):
        df.loc[(df['대학코드'] == tr_school_cd) & (df['변환표준공식번호'] == tr_cd), '탐2표점최고'] = tr2_top

    # common012 활용기준 등급점수
    df_dguk = df.loc[:, '국어등급점수1등급':'국어등급점수9등급']
    df_dsu = df.loc[:, '수학등급점수1등급':'수학등급점수9등급']
    df_dtam = df.loc[:, '탐구등급점수1등급':'탐구등급점수9등급']
    df.loc[df['국어활용기준'] == '등급점수', '국어환산점수'] = df['국어영역만점'] * df_dguk.iloc[:, guk_dsc - 1] / df_dguk.iloc[:, 0]
    df.loc[df['수학활용기준'] == '등급점수', '수학가산전'] = df['수학영역만점'] * df_dsu.iloc[:, su_dsc - 1] / df_dsu.iloc[:, 0]
    df.loc[df['탐구활용기준'] == '등급점수', '탐1가산전'] = df['탐구영역만점'] * df_dtam.iloc[:, tam1_dsc - 1] / df_dtam.iloc[:, 0]
    df.loc[df['탐구활용기준'] == '등급점수', '탐2가산전'] = df['탐구영역만점'] * df_dtam.iloc[:, tam2_dsc - 1] / df_dtam.iloc[:, 0]

# ★★★★★★★별도산출은 이 아래부터 작성할 것★★★★★★★
    # ★★★★★★★별도산출: 가천대 13201
    # code 3: 국/수 중 백분위가 높은 순으로 350, 250점 반영
    # code 4: code 3 + 기하/미적분 vs 과탐1/과탐2 중 백분위가 높은 쪽에 5% 낮은 쪽에 3%의 가산점 부여
    # code 5: 기하/미적분 vs 과탐평균 중 백분위가 높은 쪽에 5% 낮은 쪽에 3%의 가산점 부여

    # code 3
    df.loc[(df['국어원점'] > df['수학원점']) & (df['대학코드'] == 13201) & (df['수능별도산출코드'] == 3), '국어영역만점'] = 350
    df.loc[(df['국어원점'] > df['수학원점']) & (df['대학코드'] == 13201) & (df['수능별도산출코드'] == 3), '수학영역만점'] = 250
    df.loc[(df['국어원점'] <= df['수학원점']) & (df['대학코드'] == 13201) & (df['수능별도산출코드'] == 3), '국어영역만점'] = 250
    df.loc[(df['국어원점'] <= df['수학원점']) & (df['대학코드'] == 13201) & (df['수능별도산출코드'] == 3), '수학영역만점'] = 350

    # code 4 국/수 비교 파트
    if su_select != '확률과통계':
        if su_bsc >= max(tam1_bsc, tam2_bsc):
            su_13201 = su_bsc * 1.05
        else:
            su_13201 = su_bsc * 1.03
    else:
        su_13201 = su_bsc
    if guk_bsc > su_13201:
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '국어영역만점'] = 350
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '수학영역만점'] = 250
    else:
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '국어영역만점'] = 250
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '수학영역만점'] = 350

    # code 4 수/탐1/탐2 비교 후 가산점 부여 파트
    if su_bsc >= tam1_bsc and su_bsc >= tam2_bsc:
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '미적분가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '기하가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '수학가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '수학가감기준'] = '환산기준'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '탐구가감과목선택'] = '과탐'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '과학가산점'] = 3
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '탐구영역가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '탐구가감기준'] = '환산기준'
    else:
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '미적분가산점'] = 3
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '기하가산점'] = 3
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '수학가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '수학가감기준'] = '환산기준'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '탐구가감과목선택'] = '과탐'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '과학가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '탐구영역가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 4), '탐구가감기준'] = '환산기준'

    # code 5 수/탐평 비교 후 가산점 부여 파트
    if user_tam1_type == '과탐' and user_tam2_type == '과탐' and su_bsc >= (tam1_bsc + tam2_bsc) / 2:
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '미적분가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '기하가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '수학가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '수학가감기준'] = '환산기준'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '탐구가감과목선택'] = '과탐'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '탐구영역가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '탐구가감기준'] = '환산기준'
        if su_select == '기하' or su_select == '미적분':
            df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '과학가산점'] = 3
        else:
            df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '과학가산점'] = 5
    elif user_tam1_type == '과탐' and user_tam2_type == '과탐' and su_bsc < (tam1_bsc + tam2_bsc) / 2:
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '미적분가산점'] = 3
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '기하가산점'] = 3
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '수학가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '수학가감기준'] = '환산기준'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '탐구가감과목선택'] = '과탐'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '과학가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '탐구영역가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '탐구가감기준'] = '환산기준'
    else:
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '미적분가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '기하가산점'] = 5
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '수학가산점단위'] = '%'
        df.loc[(df['대학코드'] == 13201) & (df['수능별도산출코드'] == 5), '수학가감기준'] = '환산기준'
    # ☆☆☆☆☆☆☆ 가천대 별도산출 영역 종료
# ===========================가이드컷 <-> 환산점수 교체 영역 끝=================================

# ★★★★★★★별도산출: 탐구 2개 모두 과탐을 응시한 경우에만 과탐의 가산점을 부여하는 별도산출 케이스을 하단에 모음
# 과탐 응시 개수에 따라 가산점 반영 수치가 변경 되는 경우 DB에 가산점 영역 null
# 과탐을 2개 응시한 경우에는 부여 2개 미만일 때는 미부여 하는 이분법일 경우 DB에 가산점 영역을 입력 하고 과탐 2개가 안되는 케이스만 0으로 처리 하도록 할 것
    # ★★★★★★★별도산출: 삼육대(1/2) 11214
    # code 2: 탐구 2개 모두 과탐을 응시한 경우에만 3%의 과탐 가산점을 부여한다.
    # ★★★★★★★별도산출: 제주대 26101
    # code 1: 탐구 2개 모두 과탐을 응시한 경우에만 10%의 과탐 가산점을 부여한다.
    # ★★★★★★★별도산출: 창원대 25103 (1/2)
    # code 2: 탐구 2개 모두 과탐을 응시한 경우에만 10%의 과탐 가산점을 부여한다.
    # ★★★★★★★별도산출: 청주대 15208 (1/2)
    # 전 학과: 탐구 2개 모두 과탐을 응시한 경우에만 10점의 과탐 가산점을 원점기준으로 부여한다.
    # ★★★★★★★별도산출: 한국해양대 23103
    # code 1: 탐구 2개 모두 과탐을 응시한 경우에만 10%의 과탐 가산점을 부여한다.
    if user_tam1_type != '과탐' or user_tam2_type != '과탐':
        df.loc[(df['대학코드'] == 11214) & (df['수능별도산출코드'] == 2), '과학가산점'] = 0
        df.loc[(df['대학코드'] == 26101) & (df['수능별도산출코드'] == 1), '과학가산점'] = 0
        df.loc[(df['대학코드'] == 25103) & (df['수능별도산출코드'] == 2), '과학가산점'] = 0
        df.loc[(df['대학코드'] == 23103) & (df['수능별도산출코드'] == 1), '과학가산점'] = 0
        df.loc[(df['대학코드'] == 15208), '과학가산점'] = 0
    # ★★★★★★★별도산출: 한국교원대
    # code 1: 탐구과목선택 컬럼(SOONENG_TAM_GAGAM_GWAMOK_CHOICE)에 입력 되어 있는 과목 2개를 모두 응시한 경우에만 가산점 10%를 부여한다.
    # (ex. 물리학I,물리학II라고 입력되어 있을 경우 과탐 두개를 각각 물리학1+물리학2를 응시한 경우에만 가산점 부여 그 외의 경우에는 과탐 가산점 0)
    if tam1_select[:2] != '물리' or tam2_select[:2] != '물리':
        df.loc[(df['대학코드'] == 15102) & (df['수능별도산출코드'] == 1) & (df['탐구가감과목선택'] == '물리학I,물리학II'), '과학가산점'] = 0
    if tam1_select[:2] != '생명' or tam2_select[:2] != '생명':
        df.loc[(df['대학코드'] == 15102) & (df['수능별도산출코드'] == 1) & (df['탐구가감과목선택'] == '생명과학I,생명과학II'), '과학가산점'] = 0
    if tam1_select[:2] != '지구' or tam2_select[:2] != '지구':
        df.loc[(df['대학코드'] == 15102) & (df['수능별도산출코드'] == 1) & (df['탐구가감과목선택'] == '지구과학I,지구과학II'), '과학가산점'] = 0
    if tam1_select[:2] != '화학' or tam2_select[:2] != '화학':
        df.loc[(df['대학코드'] == 15102) & (df['수능별도산출코드'] == 1) & (df['탐구가감과목선택'] == '화학I,화학II'), '과학가산점'] = 0
    # ☆☆☆☆☆☆☆ 과탐 2개 응시할 경우에만 DB내 가산점 부여 별도산출 영역 종료

    # ★★★★★★★별도산출: 가톨릭관동대 14201
    # code 1: a.탐구 2개 모두 과탐을 응시하고, 화학2 or 생명과학2를 응시한 경우 탐구 2개 과목 평균의 7% 가산, b.탐구 2개 모두 과탐을 응시한 경우 탐구 2개 과목 평균의 5% 가산
    # code 2:  탐구 2개 모두 과탐을 응시한 경우 탐구 2개 과목 평균의 5% 가산
    # ★★★★★★★별도산출: 경상국립대  25102
    # code 1: a.탐구 2개 모두 과탐을 응시하고, 탐구2를 1개라도 응시한 경우 탐구 2개 과목 평균의 10% 가산, b.탐구 2개 모두 과탐을 응시한 경우 탐구 2개 과목 평균의 5% 가산
    # 14201 code 1a, 2 & 25102 code 1a : 탐구 2개 모두 과탐을 응시한 경우 탐구 2개 과목 평균의 5% 가산
    if user_tam1_type == '과탐' and user_tam2_type == '과탐':
        df.loc[((df['대학코드'] == 14201) | (df['대학코드'] == 25102)) & ((df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2)), '탐구가감과목선택'] = '과탐'
        df.loc[((df['대학코드'] == 14201) | (df['대학코드'] == 25102)) & ((df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2)), '과학가산점'] = 5
        df.loc[((df['대학코드'] == 14201) | (df['대학코드'] == 25102)) & ((df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2)), '탐구영역가산점단위'] = '%'
        df.loc[((df['대학코드'] == 14201) | (df['대학코드'] == 25102)) & ((df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2)), '탐구가감기준'] = '환산기준'
        # 14201 code 1b: 생2 or 화2를 응시한 경우 탐구 2개 과목 평균의 7% 가산
        # 25102 code 1b: 탐구2 과목을 한 개라도 응시한 경우 탐구 2개 과목 평균의 10% 가산
        if tam1_select == '화학2' or tam1_select == '생명과학2' or tam2_select == '화학2' or tam2_select == '생명과학2':
            df.loc[(df['대학코드'] == 14201) & (df['수능별도산출코드'] == 1), '과학가산점'] = 7
        else:
            df.loc[(df['대학코드'] == 14201) & (df['수능별도산출코드'] == 1), '과학가산점'] = 5
        if tam1_select == '물리학2' or tam1_select == '화학2' or tam1_select == '생명과학2' or tam1_select == '지구과학2' or tam2_select == '물리학2' or tam2_select == '화학2' or tam2_select == '생명과학2' or tam2_select == '지구과학2':
            df.loc[(df['대학코드'] == 25102) & (df['수능별도산출코드'] == 1), '과학가산점'] = 10
        else:
            df.loc[(df['대학코드'] == 25102) & (df['수능별도산출코드'] == 1), '과학가산점'] = 5
    else:
        df.loc[((df['대학코드'] == 14201) | (df['대학코드'] == 25102)) & ((df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2)), '과학가산점'] = 0
    # ☆☆☆☆☆☆☆ 가톨릭관동대, 경상국립대 별도산출 영역 종료

    #common013 탐구 가산점 부여 여부 최종 결정
    for tam1_ex, tam1_result in zip(list_tam_extras, list_tam_ex_result1):
        df.loc[df['탐구가감과목선택'] == tam1_ex, 'tam1_extra'] = tam1_result
    for tam2_ex, tam2_result in zip(list_tam_extras, list_tam_ex_result2):
        df.loc[df['탐구가감과목선택'] == tam2_ex, 'tam2_extra'] = tam2_result
    df.loc[df['tam1_extra'] == '사회가산점', 'tam1사탐가산'] = df['사회가산점']
    df.loc[df['tam1_extra'] == '사회가산점', 'tam1과탐가산'] = 0
    df.loc[df['tam1_extra'] == '과학가산점', 'tam1사탐가산'] = 0
    df.loc[df['tam1_extra'] == '과학가산점', 'tam1과탐가산'] = df['과학가산점']
    df.loc[df['tam2_extra'] == '사회가산점', 'tam2사탐가산'] = df['사회가산점']
    df.loc[df['tam2_extra'] == '사회가산점', 'tam2과탐가산'] = 0
    df.loc[df['tam2_extra'] == '과학가산점', 'tam2사탐가산'] = 0
    df.loc[df['tam2_extra'] == '과학가산점', 'tam2과탐가산'] = df['과학가산점']

    #common014 영역별 가산점 포함 원점
    df.loc[df['수학가산점단위'].isnull(), '수학가산원점'] = df['수학원점']
    df.loc[df['수학가산점단위'] == '%', '수학가산원점'] = df['수학원점'] * (1 + df[su_extra].fillna(0) / 100)
    df.loc[df['수학가산점단위'] == '점수', '수학가산원점'] = df['수학원점'] + df[su_extra].fillna(0)
    df.loc[df['탐구영역가산점단위'].isnull(), '탐1가산원점'] = df['탐1원점']
    df.loc[df['탐구영역가산점단위'] == '%', '탐1가산원점'] = df['탐1원점'] * (1 + (df['tam1사탐가산'] + df['tam1과탐가산']) / 100)
    df.loc[df['탐구영역가산점단위'] == '점수', '탐1가산원점'] = df['탐1원점'] + df['tam1사탐가산'] + df['tam1과탐가산']
    df.loc[df['탐구영역가산점단위'].isnull(), '탐2가산원점'] = df['탐2원점']
    df.loc[df['탐구영역가산점단위'] == '%', '탐2가산원점'] = df['탐2원점'] * (1 + (df['tam2사탐가산'] + df['tam2과탐가산']) / 100)
    df.loc[df['탐구영역가산점단위'] == '점수', '탐2가산원점'] = df['탐2원점'] + df['tam2사탐가산'] + df['tam2과탐가산']

    # common015 탐구 원점 평균
    df.loc[((df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산') | (df['탐구활용기준'] == '변환표준') | (
                df['탐구활용기준'] == '변표최고환산')) & (df['탐구개수'] == 2), '탐평가산원점'] = df['탐1가산원점'] + df['탐2가산원점']
    df.loc[((df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산') | (df['탐구활용기준'] == '변환표준') | (
                df['탐구활용기준'] == '변표최고환산')) & (df['탐구개수'] == 1), '탐평가산원점'] = 2 * df[['탐1가산원점', '탐2가산원점']].max(axis=1)
    df.loc[(df['탐구활용기준'] == '백분위') & (df['탐구개수'] == 2), '탐평가산원점'] = (df['탐1가산원점'] + df['탐2가산원점']) / 2
    df.loc[(df['탐구활용기준'] == '백분위') & (df['탐구개수'] == 1), '탐평가산원점'] = df[['탐1가산원점', '탐2가산원점']].max(axis=1)
    df.loc[((df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산') | (df['탐구활용기준'] == '변환표준') | (
                df['탐구활용기준'] == '변표최고환산')) & (df['탐구개수'] == 2) & (df['한국사적용기준'] == '탐구로대체'), '탐평가산원점'] \
        = df['탐1가산원점'] + df['탐2가산원점'] + df['한국사'] - df[['탐1가산원점', '탐2가산원점', '한국사']].min(axis=1)
    df.loc[((df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '표준최고환산') | (df['탐구활용기준'] == '변환표준') | (
                df['탐구활용기준'] == '변표최고환산')) & (df['탐구개수'] == 1) & (df['한국사적용기준'] == '탐구로대체'), '탐평가산원점'] \
        = 2 * df[['탐1가산원점', '탐2가산원점', '한국사']].max(axis=1)
    df.loc[(df['탐구활용기준'] == '백분위') & (df['탐구개수'] == 2) & (df['한국사적용기준'] == '탐구로대체'), '탐평가산원점'] \
        = (df['탐1가산원점'] + df['탐2가산원점'] + df['한국사'] - df[['탐1가산원점', '탐2가산원점', '한국사']].min(axis=1)) / 2
    df.loc[(df['탐구활용기준'] == '백분위') & (df['탐구개수'] == 1) & (df['한국사적용기준'] == '탐구로대체'), '탐평가산원점'] \
        = df[['탐1가산원점', '탐2가산원점', '한국사']].max(axis=1)

    #common016 탐구변롼표준점수 원점 평균
    df.loc[((df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '변표최고환산')) & (df['탐구개수'] == 2), '탐평원점'] \
        = df['탐1원점'] + df['탐2원점']
    df.loc[((df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '변표최고환산')) & (df['탐구개수'] == 1), '탐평원점'] \
        = 2 * df[['탐1원점', '탐2원점']].max(axis=1)

    #common017 영역별 원점수 순위 테이블 생성: 가산점 포함
    won_score_rank = df[['국어원점', '수학가산원점', '영어환산점수', '탐평가산원점']].rank(axis=1, method='min', na_option='bottom', ascending=False)
    won_score_rank['국wr'] = won_score_rank['국어원점'] + 0.2
    won_score_rank['수wr'] = won_score_rank['수학가산원점'] + 0
    won_score_rank['영wr'] = won_score_rank['영어환산점수'] + 0.3
    won_score_rank['탐wr'] = won_score_rank['탐평가산원점'] + 0.1
    df_won_score_rank = won_score_rank[['국wr', '수wr', '영wr', '탐wr']].rank(axis=1, method='min', na_option='bottom')

    # ★★★★★★★별도산출: 덕성여대 11210
    # code 1 : 국어, 수학, 영어, 탐구(1개) 영역 중 백분위가 높은 순으로(가산포함) 160, 140, 100, 0점씩 반영 (가산점을 포함해도 동점일 경우 랜덤)
    df.loc[((df_won_score_rank['영wr'] < df_won_score_rank['국wr']) | (df_won_score_rank['영wr'] < df_won_score_rank['수wr'])) & (df['대학코드'] == 11210) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 300
    df.loc[(df_won_score_rank['국wr'] > df_won_score_rank['영wr']) & (df_won_score_rank['국wr'] > df_won_score_rank['수wr']) & (df['대학코드'] == 11210) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 150
    df.loc[(df_won_score_rank['수wr'] > df_won_score_rank['국wr']) & (df_won_score_rank['수wr'] > df_won_score_rank['영wr']) & (df['대학코드'] == 11210) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 150
    df.loc[(df['대학코드'] == 11210) & (df['수능별도산출코드'] == 1), '영어환산점수'] = df['영어영역만점'] * df['영어'] * 0.01
    # ☆☆☆☆☆☆☆ 덕성여대 별도산출 영역 종료

    # ★★★★★★★별도산출: 대구가톨릭대 22206
    # code 1 : 국어, 수학, 영어, 탐구 영역 중 백분위가 높은 순으로(가산포함) 160, 140, 100, 0점씩 반영 (가산점을 포함해도 동점일 경우 랜덤)
    df.loc[(df_won_score_rank['국wr'] == 4) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 0
    df.loc[(df_won_score_rank['수wr'] == 4) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 0
    df.loc[(df_won_score_rank['영wr'] == 4) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 0
    df.loc[(df_won_score_rank['탐wr'] == 4) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 0
    df.loc[(df_won_score_rank['국wr'] == 3) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 100
    df.loc[(df_won_score_rank['수wr'] == 3) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 100
    df.loc[(df_won_score_rank['영wr'] == 3) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 100
    df.loc[(df_won_score_rank['탐wr'] == 3) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 100
    df.loc[(df_won_score_rank['국wr'] == 2) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 140
    df.loc[(df_won_score_rank['수wr'] == 2) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 140
    df.loc[(df_won_score_rank['영wr'] == 2) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 140
    df.loc[(df_won_score_rank['탐wr'] == 2) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 140
    df.loc[(df_won_score_rank['국wr'] == 1) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 160
    df.loc[(df_won_score_rank['수wr'] == 1) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 160
    df.loc[(df_won_score_rank['영wr'] == 1) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 160
    df.loc[(df_won_score_rank['탐wr'] == 1) & (df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 160
    df.loc[(df['대학코드'] == 22206) & (df['수능별도산출코드'] == 1), '영어환산점수'] = df['영어영역만점'] * df['영어'] * 0.01
    # ☆☆☆☆☆☆☆ 대구가톨릭대 별도산출 영역 종료

    # ★★★★★★★별도산출: 삼육대(2/2) 11214
    # code 1 : 국어, 수학, 영어, 탐구 영역 중 백분위가 높은 순으로(가산포함) 400, 300, 200, 100점씩 반영 (가산점을 포함해도 동점일 경우 랜덤)
    df.loc[(df_won_score_rank['국wr'] == 4) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 100
    df.loc[(df_won_score_rank['수wr'] == 4) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 100
    df.loc[(df_won_score_rank['영wr'] == 4) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 100
    df.loc[(df_won_score_rank['탐wr'] == 4) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 100
    df.loc[(df_won_score_rank['국wr'] == 3) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 200
    df.loc[(df_won_score_rank['수wr'] == 3) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 200
    df.loc[(df_won_score_rank['영wr'] == 3) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 200
    df.loc[(df_won_score_rank['탐wr'] == 3) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 200
    df.loc[(df_won_score_rank['국wr'] == 2) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 300
    df.loc[(df_won_score_rank['수wr'] == 2) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 300
    df.loc[(df_won_score_rank['영wr'] == 2) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 300
    df.loc[(df_won_score_rank['탐wr'] == 2) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 300
    df.loc[(df_won_score_rank['국wr'] == 1) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 400
    df.loc[(df_won_score_rank['수wr'] == 1) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 400
    df.loc[(df_won_score_rank['영wr'] == 1) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 400
    df.loc[(df_won_score_rank['탐wr'] == 1) & (df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 400
    df.loc[(df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '영어환산점수'] = df['영어영역만점'] * df['영어'] * 0.01
    df.loc[(df['대학코드'] == 11214) & (df['수능별도산출코드'] == 1), '한국사'] = df['탐구영역만점'] * df['한국사'] * 0.01 #탐구로대체 시 한국사 채택을 위해
    # ☆☆☆☆☆☆☆ 삼육대 별도산출 영역 종료

    # ★★★★★★★별도산출: 수원대 13212
    # code 1: 국어 300 반영(고정), 수학, 영어, 탐구(1과목) 중 백분위 높은 순으로 300, 250, 150 반영 (가산포함)
    score_rank13212A = df_won_score_rank[['수wr', '영wr', '탐wr']].rank(axis=1, method='min', na_option='bottom')
    df.loc[(score_rank13212A['수wr'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 300
    df.loc[(score_rank13212A['수wr'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 250
    df.loc[(score_rank13212A['수wr'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 150
    df.loc[(score_rank13212A['영wr'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 300
    df.loc[(score_rank13212A['영wr'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 250
    df.loc[(score_rank13212A['영wr'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 150
    df.loc[(score_rank13212A['탐wr'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 300
    df.loc[(score_rank13212A['탐wr'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 250
    df.loc[(score_rank13212A['탐wr'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 150
    # code 2: 수학 300 반영(고정), 국어, 영어, 탐구(1과목) 중 백분위 높은 순으로 300, 250, 150 반영 (가산포함)
    score_rank13212B = df_won_score_rank[['국wr', '영wr', '탐wr']].rank(axis=1, method='min', na_option='bottom')
    df.loc[(score_rank13212B['국wr'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '국어영역만점'] = 300
    df.loc[(score_rank13212B['국wr'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '국어영역만점'] = 250
    df.loc[(score_rank13212B['국wr'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '국어영역만점'] = 150
    df.loc[(score_rank13212B['영wr'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '영어영역만점'] = 300
    df.loc[(score_rank13212B['영wr'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '영어영역만점'] = 250
    df.loc[(score_rank13212B['영wr'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '영어영역만점'] = 150
    df.loc[(score_rank13212B['탐wr'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '탐구영역만점'] = 300
    df.loc[(score_rank13212B['탐wr'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '탐구영역만점'] = 250
    df.loc[(score_rank13212B['탐wr'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 2), '탐구영역만점'] = 150
    # code 3: 국어, 수학, 영어, 탐구(1과목) 성적 순으로 450, 350, 200, 0 점 반영 (가산미포함)
    score_rank13212 = df[['국어원점', '수학원점', '영어환산점수', '탐평원점']].rank(axis=1, method='min', na_option='bottom', ascending=False)
    score_rank13212['국'] = score_rank13212['국어원점'] + 0.2
    score_rank13212['수'] = score_rank13212['수학원점'] + 0
    score_rank13212['영'] = score_rank13212['영어환산점수'] + 0.3
    score_rank13212['탐'] = score_rank13212['탐평원점'] + 0.1
    df_score_rank13212 = score_rank13212[['국', '수', '영', '탐']].rank(axis=1, method='min', na_option='bottom', ascending=True)
    df.loc[(df_score_rank13212['국'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '국어영역만점'] = 450
    df.loc[(df_score_rank13212['국'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '국어영역만점'] = 350
    df.loc[(df_score_rank13212['국'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '국어영역만점'] = 200
    df.loc[(df_score_rank13212['국'] == 4) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '국어영역만점'] = 0
    df.loc[(df_score_rank13212['수'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '수학영역만점'] = 450
    df.loc[(df_score_rank13212['수'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '수학영역만점'] = 350
    df.loc[(df_score_rank13212['수'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '수학영역만점'] = 200
    df.loc[(df_score_rank13212['수'] == 4) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '수학영역만점'] = 0
    df.loc[(df_score_rank13212['영'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '영어영역만점'] = 450
    df.loc[(df_score_rank13212['영'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '영어영역만점'] = 350
    df.loc[(df_score_rank13212['영'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '영어영역만점'] = 200
    df.loc[(df_score_rank13212['영'] == 4) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '영어영역만점'] = 0
    df.loc[(df_score_rank13212['탐'] == 1) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '탐구영역만점'] = 450
    df.loc[(df_score_rank13212['탐'] == 2) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '탐구영역만점'] = 350
    df.loc[(df_score_rank13212['탐'] == 3) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '탐구영역만점'] = 200
    df.loc[(df_score_rank13212['탐'] == 4) & (df['대학코드'] == 13212) & (df['수능별도산출코드'] == 3), '탐구영역만점'] = 0
    df.loc[df['대학코드'] == 13212, '영어환산점수'] = df['영어영역만점'] * df['영어'] * 0.01
    # ☆☆☆☆☆☆☆ 수원대 별도산출 영역 종료

    # ★★★★★★★별도산출: 한성대 11234
    # code 1 : 국어, 수학, 영어, 탐구 영역 중 백분위가 높은 순으로(가산포함) 400, 300, 200, 100점씩 반영 (가산점을 포함해도 동점일 경우 랜덤)
    df.loc[(df_won_score_rank['국wr'] == 4) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 100
    df.loc[(df_won_score_rank['수wr'] == 4) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 100
    df.loc[(df_won_score_rank['영wr'] == 4) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 100
    df.loc[(df_won_score_rank['탐wr'] == 4) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 100
    df.loc[(df_won_score_rank['국wr'] == 3) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 200
    df.loc[(df_won_score_rank['수wr'] == 3) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 200
    df.loc[(df_won_score_rank['영wr'] == 3) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 200
    df.loc[(df_won_score_rank['탐wr'] == 3) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 200
    df.loc[(df_won_score_rank['국wr'] == 2) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 300
    df.loc[(df_won_score_rank['수wr'] == 2) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 300
    df.loc[(df_won_score_rank['영wr'] == 2) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 300
    df.loc[(df_won_score_rank['탐wr'] == 2) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 300
    df.loc[(df_won_score_rank['국wr'] == 1) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '국어영역만점'] = 400
    df.loc[(df_won_score_rank['수wr'] == 1) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '수학영역만점'] = 400
    df.loc[(df_won_score_rank['영wr'] == 1) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '영어영역만점'] = 400
    df.loc[(df_won_score_rank['탐wr'] == 1) & (df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '탐구영역만점'] = 400
    df.loc[(df['대학코드'] == 11234) & (df['수능별도산출코드'] == 1), '영어환산점수'] = df['영어영역만점'] * df['영어'] * 0.01
    # ☆☆☆☆☆☆☆ 한성대 별도산출 영역 종료

    # ★★★★★★★별도산출: 한신대 13227
    # code 1 : 국어, 수학, 영어 영역 중 백분위가 높은 순으로(가산포함) 500, 300, 200점씩 반영 (가산점을 포함해도 동점일 경우 랜덤)
    df.loc[(df_won_score_rank['국wr'] == 4) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '국어영역만점'] = 0
    df.loc[(df_won_score_rank['수wr'] == 4) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '수학영역만점'] = 0
    df.loc[(df_won_score_rank['영wr'] == 4) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '영어영역만점'] = 0
    df.loc[(df_won_score_rank['탐wr'] == 4) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '탐구영역만점'] = 0
    df.loc[(df_won_score_rank['국wr'] == 3) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '국어영역만점'] = 200
    df.loc[(df_won_score_rank['수wr'] == 3) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '수학영역만점'] = 200
    df.loc[(df_won_score_rank['영wr'] == 3) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '영어영역만점'] = 200
    df.loc[(df_won_score_rank['탐wr'] == 3) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '탐구영역만점'] = 200
    df.loc[(df_won_score_rank['국wr'] == 2) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '국어영역만점'] = 300
    df.loc[(df_won_score_rank['수wr'] == 2) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '수학영역만점'] = 300
    df.loc[(df_won_score_rank['영wr'] == 2) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '영어영역만점'] = 300
    df.loc[(df_won_score_rank['탐wr'] == 2) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '탐구영역만점'] = 300
    df.loc[(df_won_score_rank['국wr'] == 1) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '국어영역만점'] = 500
    df.loc[(df_won_score_rank['수wr'] == 1) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '수학영역만점'] = 500
    df.loc[(df_won_score_rank['영wr'] == 1) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '영어영역만점'] = 500
    df.loc[(df_won_score_rank['탐wr'] == 1) & (df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '탐구영역만점'] = 500
    df.loc[(df['대학코드'] == 13227) & (df['수능별도산출코드'].notnull()), '영어환산점수'] = df['영어영역만점'] * df['영어'] * 0.01
    # ☆☆☆☆☆☆☆ 한신대 별도산출 영역 종료

    #common018 가산전 영역별 환산점수: 국어 환산점수 완료
    df.loc[df['국어활용기준'] == '백분위', '국어환산점수'] = df['국어영역만점'] * df['국어원점'] / 100
    df.loc[df['국어활용기준'] == '표준점수', '국어환산점수'] = df['국어영역만점'] * df['국어원점'] / 200
    df.loc[df['국어활용기준'] == '표준최고환산', '국어환산점수'] = df['국어영역만점'] * df['국어원점'] / top_scr_guk
    df.loc[df['수학활용기준'] == '백분위', '수학가산전'] = df['수학영역만점'] * df['수학원점'] / 100
    df.loc[df['수학활용기준'] == '표준점수', '수학가산전'] = df['수학영역만점'] * df['수학원점'] / 200
    df.loc[df['수학활용기준'] == '표준최고환산', '수학가산전'] = df['수학영역만점'] * df['수학원점'] / top_scr_su
    df.loc[(df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '백분위'), '탐1가산전'] = df['탐구영역만점'] * df['탐1원점'] / 100
    df.loc[(df['탐구활용기준'] == '표준최고환산') | (df['탐구활용기준'] == '변표최고환산'), '탐1가산전'] = df['탐구영역만점'] * df['탐1원점'] / df['탐1표점최고']
    df.loc[(df['탐구활용기준'] == '표준점수') | (df['탐구활용기준'] == '변환표준') | (df['탐구활용기준'] == '백분위'), '탐2가산전'] = df['탐구영역만점'] * df['탐2원점'] / 100
    df.loc[(df['탐구활용기준'] == '표준최고환산') | (df['탐구활용기준'] == '변표최고환산'), '탐2가산전'] = df['탐구영역만점'] * df['탐2원점'] / df['탐2표점최고']

    #common019 영역별 가산점 (환산 후)
    df.loc[(df['수학가산점단위'] == '%') & (df['수학가감기준'] == '환산기준'), '수학가산점'] = df['수학가산전'] * df[su_extra] / 100
    df.loc[(df['수학가산점단위'] == '%') & (df['수학가감기준'] == '원점기준'), '수학가산점'] = df['수학원점'] * df[su_extra] / 100
    df.loc[df['수학가산점단위'] == '점수', '수학가산점'] = df[su_extra]
    df.loc[(df['탐구영역가산점단위'] == '%') & (df['탐구가감기준'] == '환산기준'), '탐1가산점'] = df['탐1가산전'] * (df['tam1사탐가산'] + df['tam1과탐가산']) / 100
    df.loc[(df['탐구영역가산점단위'] == '%') & (df['탐구가감기준'] == '원점기준'), '탐1가산점'] = df['탐1원점'] * (df['tam1사탐가산'] + df['tam1과탐가산']) / 100
    df.loc[df['탐구영역가산점단위'] == '점수', '탐1가산점'] = df['tam1사탐가산'] + df['tam1과탐가산']
    df.loc[(df['탐구영역가산점단위'] == '%') & (df['탐구가감기준'] == '환산기준'), '탐2가산점'] = df['탐2가산전'] * (df['tam2사탐가산'] + df['tam2과탐가산']) / 100
    df.loc[(df['탐구영역가산점단위'] == '%') & (df['탐구가감기준'] == '원점기준'), '탐2가산점'] = df['탐2원점'] * (df['tam2사탐가산'] + df['tam2과탐가산']) / 100
    df.loc[df['탐구영역가산점단위'] == '점수', '탐2가산점'] = df['tam2사탐가산'] + df['tam2과탐가산']

    # ★★★★★★★별도산출: 부경대 23101
    # code 1: 과탐2 영역에는 10% 가산, 과탐1에는 6% 가산 (원점기준)
    if user_tam1_type == '과탐':
        if tam1_select[-1:] == '2':
            df.loc[(df['대학코드'] == 23101) & (df['수능별도산출코드'] == 1), '탐1가산점'] = df['탐1원점'] * 0.1
        else:
            df.loc[(df['대학코드'] == 23101) & (df['수능별도산출코드'] == 1), '탐1가산점'] = df['탐1원점'] * 0.06
    else:
        df.loc[(df['대학코드'] == 23101) & (df['수능별도산출코드'] == 1), '탐1가산점'] = 0
    if user_tam2_type == '과탐':
        if tam2_select[-1:] == '2':
            df.loc[(df['대학코드'] == 23101) & (df['수능별도산출코드'] == 1), '탐2가산점'] = df['탐2원점'] * 0.1
        else:
            df.loc[(df['대학코드'] == 23101) & (df['수능별도산출코드'] == 1), '탐2가산점'] = df['탐2원점'] * 0.06
    else:
        df.loc[(df['대학코드'] == 23101) & (df['수능별도산출코드'] == 1), '탐2가산점'] = 0
    # ☆☆☆☆☆☆☆ 부경대 별도산출 영역 종료

    # ★★★★★★★별도산출: 을지대 13219
    # code 1: 탐구 2개 모두 과탐을 응시하면 5%, 탐구 1개만 과탐을 응시하면 3% 가산
    if user_tam1_type == '과탐' and user_tam2_type == '과탐':
        df.loc[(df['대학코드'] == 13219) & (df['수능별도산출코드'] == 1), '탐1가산점'] = df['탐1가산전'] * 0.05
        df.loc[(df['대학코드'] == 13219) & (df['수능별도산출코드'] == 1), '탐2가산점'] = df['탐2가산전'] * 0.05
    elif user_tam1_type == '과탐' or user_tam2_type == '과탐':
        df.loc[(df['대학코드'] == 13219) & (df['수능별도산출코드'] == 1), '탐1가산점'] = df['탐1가산전'] * 0.03
        df.loc[(df['대학코드'] == 13219) & (df['수능별도산출코드'] == 1), '탐2가산점'] = df['탐2가산전'] * 0.03
    # ☆☆☆☆☆☆☆ 을지대 별도산출 영역 종료

    # ★★★★★★★별도산출: 창원대 25103 (2/2)
    # code 1: 수능기본점수를 모든 점수 계산 후 최종 시점에 더하지 않고 영역별로 쪼개 각 영역 환산점수에 미리 합산한 후 가산점 부여
    # 영역별기본점 = 해당영역만점/(수능만점-수능기본점) * 수능기본점
    # code 2: code 1 + 탐구 2개 모두 '과탐'을 응시한 경우에만 가산점 부여 (위의 과탐2개 온리 가산점 파트에서 해결)
    df['수학기본점'] = df['수학영역만점'] / (df['수능만점'] - df['수능기본점수']) * df['수능기본점수']
    df['탐구기본점'] = df['탐구영역만점'] / (df['수능만점'] - df['수능기본점수']) * df['수능기본점수']
    df.loc[(df['대학코드'] == 25103) & (df['수능별도산출코드'] == 1), '수학가산점'] = (df['수학가산전'] + df['수학기본점']) * df[su_extra] / 100
    df.loc[(df['대학코드'] == 25103) & (df['수능별도산출코드'] == 2), '탐1가산점'] = (df['탐1가산전'] + df['탐구기본점']) * df['tam1과탐가산'] / 100
    df.loc[(df['대학코드'] == 25103) & (df['수능별도산출코드'] == 2), '탐2가산점'] = (df['탐2가산전'] + df['탐구기본점']) * df['tam2과탐가산'] / 100
    # ☆☆☆☆☆☆☆ 창원대 별도산출 영역 종료

    # ★★★★★★★별도산출: 한경대 13101
    # code 1: 과탐II 과목 중 하나를 응시한 경우 15% 가산, 과탐I 과목 중 하나를 응시한 경우 10% 가산 (환산기준)
    if user_tam1_type == '과탐':
        if tam1_select[-1:] == '2':
            df.loc[(df['대학코드'] == 13101) & (df['수능별도산출코드'] == 1), '탐1가산점'] = df['탐1가산전'] * 0.15
        else:
            df.loc[(df['대학코드'] == 13101) & (df['수능별도산출코드'] == 1), '탐1가산점'] = df['탐1가산전'] * 0.1
    else:
        df.loc[(df['대학코드'] == 13101) & (df['수능별도산출코드'] == 1), '탐1가산점'] = 0
    if user_tam2_type == '과탐':
        if tam2_select[-1:] == '2':
            df.loc[(df['대학코드'] == 13101) & (df['수능별도산출코드'] == 1), '탐2가산점'] = df['탐2가산전'] * 0.15
        else:
            df.loc[(df['대학코드'] == 13101) & (df['수능별도산출코드'] == 1), '탐2가산점'] = df['탐2가산전'] * 0.1
    else:
        df.loc[(df['대학코드'] == 13101) & (df['수능별도산출코드'] == 1), '탐2가산점'] = 0
    # ☆☆☆☆☆☆☆ 한경대 별도산출 영역 종료

    # ★★★★★★★별도산출: 성신여대 11222
    # code 1: 탐구 가감 과목 선택 열에 입력 된 과목에 속하는 응시자 탐구 성적 2개 중 백분위가 높은 한 과목에 원점 기준으로 가산(수학 가산점은 일반 로직을 따른다.)
    # '가산미포함' 선택이므로 탐구영역을 선택할 때 가산점은 고려되지 않는다.
    # 해당 과목 채택 여부와 상관없이 탐구 1,2 중 높은 값의 백분위 기준 가산점을 반영한다.
    df.loc[(df['대학코드'] == 11222) & (df['수능별도산출코드'] == 1) & (df['탐1가산점'] < df['탐2가산점']), '탐1가산점'] = 0
    df.loc[(df['대학코드'] == 11222) & (df['수능별도산출코드'] == 1) & (df['탐1가산점'] >= df['탐2가산점']), '탐2가산점'] = 0
    # ☆☆☆☆☆☆☆ 성신여대 별도산출 영역 종료

    # ★★★★★★★별도산출: 세명대 15205
    # code 1: 한국사와 영어 중 등급이 높은 쪽을 영어 점수로 반영한다. (한국사 적용기준은 '별도산출'로 입력 하였음)
    df.loc[(df['대학코드'] == 15205) & (df['수능별도산출코드'] == 1) & (df['한국사'] > df['영어']), '영어환산점수'] = df['한국사']
    #df.loc[(df['대학코드'] == 15205) & (df['수능별도산출코드'] == 1) & (df['한국사'] <= df['영어']), '영어환산점수'] = df['영어']
    # code 2: 탐구 2개 모두 과탐을 응시한 경우에만 가산점을 부여한다.
    if user_tam1_type != '과탐' or user_tam2_type != '과탐':
        df.loc[(df['대학코드'] == 15205) & (df['수능별도산출코드'] == 2), '탐1가산점'] = 0
        df.loc[(df['대학코드'] == 15205) & (df['수능별도산출코드'] == 2), '탐2가산점'] = 0
    # ☆☆☆☆☆☆☆ 세명대 별도산출 영역 종료

    # ★★★★★★★별도산출: 숭실대 11225
    # code 1: 탐구는 변환표준점수를 사용하나 가산점은 변환표준점수 기준이 아닌 '백분위'기준으로 반영한다. (원점기준)
    df.loc[(df['대학코드'] == 11225) & (df['수능별도산출코드'] == 1), '탐1가산점'] = tam1_bsc * (df['tam1사탐가산'] + df['tam1과탐가산']) / 100
    df.loc[(df['대학코드'] == 11225) & (df['수능별도산출코드'] == 1), '탐2가산점'] = tam2_bsc * (df['tam2사탐가산'] + df['tam2과탐가산']) / 100
    # ☆☆☆☆☆☆☆ 숭실대 별도산출 영역 종료

    #common020 가산점 합산: 수학 환산점수 완료, 탐1, 탐2 환산점수 완료
    df['수학환산점수'] = df['수학가산전'].fillna(0) + df['수학가산점'].fillna(0)
    df['탐1환산점수'] = df['탐1가산전'].fillna(0) + df['탐1가산점'].fillna(0)
    df['탐2환산점수'] = df['탐2가산전'].fillna(0) + df['탐2가산점'].fillna(0)

    #common021 탐구 1개 반영일 때 평균
    df.loc[(df['탐구개수'] == 1) & (df['한국사적용기준'] != '탐구로대체') & (df['제2외/한적용기준'] != '탐구로대체'), '탐구환산점수'] \
        = df.loc[:, ['탐1환산점수', '탐2환산점수']].max(axis=1)
    df.loc[(df['탐구개수'] == 1) & (df['한국사적용기준'] == '탐구로대체') & (df['제2외/한적용기준'] != '탐구로대체'), '탐구환산점수'] \
        = df.loc[:, ['탐1환산점수', '탐2환산점수','한국사']].max(axis=1)
    df.loc[(df['탐구개수'] == 1) & (df['한국사적용기준'] != '탐구로대체') & (df['제2외/한적용기준'] == '탐구로대체'), '탐구환산점수'] \
        = df.loc[:, ['탐1환산점수', '탐2환산점수', '제2외']].max(axis=1)
    # 탐구 2개 반영일 때 평균
    df.loc[(df['탐구개수'] == 2) & (df['한국사적용기준'] != '탐구로대체') & (df['제2외/한적용기준'] != '탐구로대체'), '탐구환산점수'] \
        = (df['탐1환산점수'] + df['탐2환산점수']) / 2
    df.loc[(df['탐구개수'] == 2) & (df['한국사적용기준'] == '탐구로대체') & (df['제2외/한적용기준'] != '탐구로대체'), '탐구환산점수'] \
        = (df['탐1환산점수'] + df['탐2환산점수'] + df['한국사'] - df.loc[:, ['탐1환산점수', '탐2환산점수', '한국사']].min(axis=1)) / 2
    df.loc[(df['탐구개수'] == 2) & (df['한국사적용기준'] != '탐구로대체') & (df['제2외/한적용기준'] == '탐구로대체'), '탐구환산점수'] \
        = (df['탐1환산점수'] + df['탐2환산점수'] + df['제2외'] - df.loc[:, ['탐1환산점수', '탐2환산점수', '제2외']].min(axis=1)) / 2

    # ★★★★★★★별도산출: 건국대(글로컬) 15201
    # code 1: 가산점을 포함한 점수가 영역만점을 넘을 경우 영역만점으로 반영한다.
    df.loc[(df['대학코드'] == 15201) & (df['수학환산점수'] > df['수학영역만점']), '수학환산점수'] = df['수학영역만점']
    df.loc[(df['대학코드'] == 15201) & (df['탐구환산점수'] > df['탐구영역만점']), '탐구환산점수'] = df['탐구영역만점']
    # ☆☆☆☆☆☆☆ 건국대(글로컬) 별도산출 영역 종료

    #common022 환산점수 영역별 점수 순위 테이블 생성: 가산점 포함
    calculation = df[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']]
    rank_1st = calculation.rank(axis=1, method='min', na_option='bottom', ascending=False)
    rank_1st['국어'] = rank_1st['국어환산점수'] + 0.2
    rank_1st['수학'] = rank_1st['수학환산점수'] + 0
    rank_1st['영어'] = rank_1st['영어환산점수'] + 0.3
    rank_1st['탐구'] = rank_1st['탐구환산점수'] + 0.1
    rank_2nd = rank_1st[['국어', '수학', '영어', '탐구']]
    rank_final = rank_2nd.rank(axis=1, method='min', na_option='bottom')
    rank_final.rename(columns={'국어': '국어rank', '수학': '수학rank', '영어': '영어rank', '탐구': '탐구rank'}, inplace=True)
    df_rank = pd.concat([calculation, rank_final], axis=1)
    df_rank.loc[df_rank['국어rank'] == 1, 'rank01'] = df_rank['국어환산점수']
    df_rank.loc[df_rank['국어rank'] == 2, 'rank02'] = df_rank['국어환산점수']
    df_rank.loc[df_rank['국어rank'] == 3, 'rank03'] = df_rank['국어환산점수']
    df_rank.loc[df_rank['국어rank'] == 4, 'rank04'] = df_rank['국어환산점수']
    df_rank.loc[df_rank['수학rank'] == 1, 'rank01'] = df_rank['수학환산점수']
    df_rank.loc[df_rank['수학rank'] == 2, 'rank02'] = df_rank['수학환산점수']
    df_rank.loc[df_rank['수학rank'] == 3, 'rank03'] = df_rank['수학환산점수']
    df_rank.loc[df_rank['수학rank'] == 4, 'rank04'] = df_rank['수학환산점수']
    df_rank.loc[df_rank['영어rank'] == 1, 'rank01'] = df_rank['영어환산점수']
    df_rank.loc[df_rank['영어rank'] == 2, 'rank02'] = df_rank['영어환산점수']
    df_rank.loc[df_rank['영어rank'] == 3, 'rank03'] = df_rank['영어환산점수']
    df_rank.loc[df_rank['영어rank'] == 4, 'rank04'] = df_rank['영어환산점수']
    df_rank.loc[df_rank['탐구rank'] == 1, 'rank01'] = df_rank['탐구환산점수']
    df_rank.loc[df_rank['탐구rank'] == 2, 'rank02'] = df_rank['탐구환산점수']
    df_rank.loc[df_rank['탐구rank'] == 3, 'rank03'] = df_rank['탐구환산점수']
    df_rank.loc[df_rank['탐구rank'] == 4, 'rank04'] = df_rank['탐구환산점수']
    df_result = pd.concat([df, df_rank[['rank01', 'rank02', 'rank03', 'rank04']]], axis=1)

    # ★★★★★★★별도산출: 경희대 11206 (예체능)
    # code 1: 탐구영역만점*(탐구변환표준점수+100)/탐구원점기준만점*0.5 = (공통식 탐구환산점수+탐구영역만점)/2
    df_result.loc[(df_result['대학코드'] == 11206) & (df_result['수능별도산출코드'] == 1), '탐구환산점수'] = (df['탐구환산점수'] + df['탐구영역만점']) / 2
    # ☆☆☆☆☆☆☆ 경희대 별도산출 영역 종료

    # ★★★★★★★별도산출: 고려대(세종) 17202 (1/2)
    # code 1
    # 국어환산점수: 수능총점x(국어표점*국어영역만점) / (국어최고표점*국어영역만점+수학최고표점*수학영역만점+영어최고표점*영어영역만점+탐구1,2최고점의 합*탐구영역만점)
    # 수학환산점수: 수능총점x(수학표점*수학영역만점) / (국어최고표점*국어영역만점+수학최고표점*수학영역만점+영어최고표점*영어영역만점+탐구1,2최고점의 합*탐구영역만점)
    # 영어환산점수: 수능총점x(영어등급점수*영어영역만점) / (국어최고표점*국어영역만점+수학최고표점*수학영역만점+영어최고표점*영어영역만점+탐구1,2최고점의 합*탐구영역만점)
    # 탐구환산점수: 수능총점x(탐구1표점+탐구2표점)*탐구영역만점 / (국어최고표점*국어영역만점+수학최고표점*수학영역만점+영어최고표점*영어영역만점+탐구1,2최고점의 합*탐구영역만점)
    # 환산점수기준 수학 가산점: 수학환산점수*수학가산점비율
    df_result.loc[df['대학코드'] == 17202, '국어환산점수'] = df['수능만점'] * df['국어원점'] * df['국어영역만점'] / (top_scr_guk * df['국어영역만점'] + top_scr_su * df['수학영역만점'] + 100 * df['영어영역만점'] + (df['탐1표점최고'] + df['탐2표점최고']) * df['탐구영역만점'])
    df_result.loc[df['대학코드'] == 17202, '수학환산점수'] = df['수능만점'] * df['수학원점'] * df['수학영역만점'] / (top_scr_guk * df['국어영역만점'] + top_scr_su * df['수학영역만점'] + 100 * df['영어영역만점'] + (df['탐1표점최고'] + df['탐2표점최고']) * df['탐구영역만점'])
    df_result.loc[df['대학코드'] == 17202, '영어환산점수'] = df['수능만점'] * df['영어환산점수'] * df['영어영역만점'] / (top_scr_guk * df['국어영역만점'] + top_scr_su * df['수학영역만점'] + 100 * df['영어영역만점'] + (df['탐1표점최고'] + df['탐2표점최고']) * df['탐구영역만점'])
    df_result.loc[df['대학코드'] == 17202, '탐구환산점수'] = df['수능만점'] * (df['탐1원점'] + df['탐2원점']) * df['탐구영역만점'] / (top_scr_guk * df['국어영역만점'] + top_scr_su * df['수학영역만점'] + 100 * df['영어영역만점'] + (df['탐1표점최고'] + df['탐2표점최고']) * df['탐구영역만점'])
    # ☆☆☆☆☆☆☆ 고려대(세종) 별도산출 (1/2) 영역 종료

    # ★★★★★★★별도산출: 인하대 12202
    # code 1: 탐구영역만점*(탐구변환표준점수+100)/(탐구변환표준점수최고점+100)
    df_result.loc[(df_result['대학코드'] == 12202) & (df_result['수능별도산출코드'] == 1), '탐구환산점수'] \
        = df['탐구영역만점'] * 0.5 * ((df['탐1원점'] + 100) / (df['탐1표점최고'] + 100) + (df['탐2원점'] + 100) / (df['탐2표점최고'] + 100))
    # ☆☆☆☆☆☆☆ 인하대 별도산출 영역 종료

    # ★★★★★★★별도산출: 충북대 15101
    # code 1: 탐구환산점수 = 탐구영역만점 * (탐구1표준점수+탐구1표준점수)/(탐구1표준최고점+탐구2표준최고점)
    # code 2: code1 + 탐구1, 탐구2 중 과탐 개수에 따라 아래와 같이 가산점 반영
    # 과탐 1개 응시한 경우: 과탐1개의 가산점과 사탐1개의 가산점(=0점)의 평균 가산점 반영 (탐구 가산점 공통식을 따름)
    # 과탐 2개 응시한 경우: 별도코드1 방식대로 계산한 탐구 점수에 DB과탐 가산점 반영
    # (탐구1표준점수+탐구1표준점수)/(탐구1표준최고점+탐구2표준최고점)
    df.loc[df['대학코드'] == 15101, '탐구환산점수'] = df['탐구영역만점'] * ((df['탐1원점'] + df['탐2원점']) / (df['탐1표점최고'] + df['탐2표점최고']))
    df_result.loc[(df['대학코드'] == 15101) & (df['수능별도산출코드'] == 1), '탐구환산점수'] = df['탐구환산점수']
    if user_tam1_type == '과탐' and user_tam2_type == '과탐':
        df_result.loc[(df['대학코드'] == 15101) & (df['수능별도산출코드'] == 2), '탐구환산점수'] = df['탐구환산점수'] * (1 + df['과학가산점'] * 0.01)
    else:
        df_result.loc[(df['대학코드'] == 15101) & (df['수능별도산출코드'] == 2), '탐구환산점수'] = df['탐구환산점수'] + (df['탐1가산점'].fillna(0) + df['탐2가산점'].fillna(0)) / 2
    # ☆☆☆☆☆☆☆ 충북대 별도산출 영역 종료

    #common023 조합별 합계 방식
    # 영어가산점인 경우 + 한국사 + 제2외 + 수능 기본점
    plus_ect = df_result[['한국사환산점수', '제2외환산점수', '수능기본점수']].sum(axis=1)
    # 국수영탐, 국수영, 국수탐, 국영탐, 수영탐, 국수, 국영, 국탐, 수영, 수탐, 영탐, 국, 수, 영, 탐
    df_result.loc[df['산출번호'] == 0, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1) + plus_ect
    # 국/수/영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 1, '환산점수'] = df_result['rank01'] + plus_ect
    # 국/수/영 중 택1
    df_result.loc[df_result['산출번호'] == 2, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수']].max(axis=1) + plus_ect
    # 국/수/탐 중 택1
    df_result.loc[df_result['산출번호'] == 3, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '탐구환산점수']].max(axis=1) + plus_ect
    # 국/영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 4, '환산점수'] = df_result[['국어환산점수', '영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect
    # 국/탐 중 택1
    df_result.loc[df_result['산출번호'] == 5, '환산점수'] = df_result[['국어환산점수', '탐구환산점수']].max(axis=1) + plus_ect
    # 국/수 중 택1
    df_result.loc[df_result['산출번호'] == 6, '환산점수'] = df_result[['국어환산점수', '수학환산점수']].max(axis=1) + plus_ect
    # 국/영 중 택1
    df_result.loc[df_result['산출번호'] == 7, '환산점수'] = df_result[['국어환산점수', '영어환산점수']].max(axis=1) + plus_ect
    # 수/영 중 택1
    df_result.loc[df_result['산출번호'] == 8, '환산점수'] = df_result[['수학환산점수', '영어환산점수']].max(axis=1) + plus_ect
    # 수/탐 중 택1
    df_result.loc[df_result['산출번호'] == 9, '환산점수'] = df_result[['수학환산점수', '탐구환산점수']].max(axis=1) + plus_ect
    # 수/영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 10, '환산점수'] = df_result[['수학환산점수', '영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect
    # 영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 11, '환산점수'] = df_result[['영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect
    # 국수+영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 12, '환산점수'] = df_result[['영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect \
                                                     + df_result[['국어환산점수', '수학환산점수']].sum(axis=1)
    # 국영+수/탐 중 택1
    df_result.loc[df_result['산출번호'] == 13, '환산점수'] = df_result[['수학환산점수', '탐구환산점수']].max(axis=1) + plus_ect \
                                                     + df_result[['국어환산점수', '영어환산점수']].sum(axis=1)
    # 국탐+수/영 중 택1
    df_result.loc[df_result['산출번호'] == 14, '환산점수'] = df_result[['수학환산점수', '영어환산점수']].max(axis=1) + plus_ect \
                                                     + df_result[['국어환산점수', '탐구환산점수']].sum(axis=1)
    # 국+수/영/탐 중 택2
    df_result.loc[df_result['산출번호'] == 15, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1) \
                                                     + plus_ect - df_result[['수학환산점수', '영어환산점수', '탐구환산점수']].min(axis=1)
    # 국+ 수/영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 16, '환산점수'] = df_result[['수학환산점수', '영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect + \
                                                     df_result['국어환산점수']
    # 국+수/영 중 택1
    df_result.loc[df_result['산출번호'] == 17, '환산점수'] = df_result[['수학환산점수', '영어환산점수']].max(axis=1) + plus_ect + df_result['국어환산점수']
    # 국+수/탐 중 택1
    df_result.loc[df_result['산출번호'] == 18, '환산점수'] = df_result[['수학환산점수', '탐구환산점수']].max(axis=1) + plus_ect + df_result['국어환산점수']

    # 국+영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 19, '환산점수'] = df_result[['영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect + df_result['국어환산점수']
    # 국/수/영/탐 중 택3
    df_result.loc[df_result['산출번호'] == 20, '환산점수'] = df_result[['rank01', 'rank02', 'rank03']].sum(axis=1) + plus_ect
    # 수영+국/탐 중 택1
    df_result.loc[df_result['산출번호'] == 21, '환산점수'] = df_result[['국어환산점수', '탐구환산점수']].max(axis=1) + plus_ect \
                                                     + df_result['수학환산점수'] + df_result['영어환산점수']
    # 수탐+국/영 중 택1
    df_result.loc[df_result['산출번호'] == 22, '환산점수'] = df_result[['국어환산점수', '영어환산점수']].max(axis=1) + plus_ect \
                                                     + df_result['수학환산점수'] + df_result['탐구환산점수']
    # 수+국/영/탐 중 택2
    df_result.loc[df_result['산출번호'] == 23, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1) \
                                                     + plus_ect - df_result[['국어환산점수', '영어환산점수', '탐구환산점수']].min(axis=1)
    # 수+국/영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 24, '환산점수'] = df_result[['국어환산점수', '영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect + \
                                                     df_result['수학환산점수']
    # 수+국/영 중 택1
    df_result.loc[df_result['산출번호'] == 25, '환산점수'] = df_result[['국어환산점수', '영어환산점수']].max(axis=1) + plus_ect \
                                                     + df_result['수학환산점수']
    # 수+국/탐 중 택1
    df_result.loc[df_result['산출번호'] == 26, '환산점수'] = df_result[['국어환산점수', '탐구환산점수']].max(axis=1) + plus_ect \
                                                     + df_result['수학환산점수']
    # 수+영/탐 중 택1
    df_result.loc[df_result['산출번호'] == 27, '환산점수'] = df_result[['영어환산점수', '탐구환산점수']].max(axis=1) + plus_ect \
                                                     + df_result['수학환산점수']
    # 영탐+국/수 중 택1
    df_result.loc[df_result['산출번호'] == 28, '환산점수'] = df_result[['국어환산점수', '수학환산점수']].max(axis=1) + plus_ect \
                                                     + df_result['영어환산점수'] + df_result['탐구환산점수']
    # 영+국/수/탐 중 택2
    df_result.loc[df_result['산출번호'] == 29, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1) \
                                                     + plus_ect - df_result[['국어환산점수', '수학환산점수', '탐구환산점수']].min(axis=1)
    # 영+국/수/탐 중 택1
    df_result.loc[df_result['산출번호'] == 30, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '탐구환산점수']].max(axis=1) + plus_ect + \
                                                     df_result['영어환산점수']
    # 영+국/수 중 택1
    df_result.loc[df_result['산출번호'] == 31, '환산점수'] = df_result[['국어환산점수', '수학환산점수']].max(axis=1) + plus_ect + df_result['영어환산점수']
    # 영+수/탐 중 택1
    df_result.loc[df_result['산출번호'] == 32, '환산점수'] = df_result[['수학환산점수', '탐구환산점수']].max(axis=1) + plus_ect + df_result['영어환산점수']
    # 영+국/탐 중 택1
    df_result.loc[df_result['산출번호'] == 33, '환산점수'] = df_result[['국어환산점수', '탐구환산점수']].max(axis=1) + plus_ect + df_result['영어환산점수']
    # 국/수/영/탐 중 택2
    df_result.loc[df_result['산출번호'] == 34, '환산점수'] = df_result[['rank01', 'rank02']].sum(axis=1) + plus_ect
    # 국/수/영 중 택2
    df_result.loc[df_result['산출번호'] == 35, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수']].sum(axis=1) + plus_ect - \
                                                     df_result[['국어환산점수', '수학환산점수', '영어환산점수']].min(axis=1)
    # 국/수/탐 중 택2
    df_result.loc[df_result['산출번호'] == 36, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '탐구환산점수']].sum(axis=1) + plus_ect - \
                                                     df_result[['국어환산점수', '수학환산점수', '탐구환산점수']].min(axis=1)
    # 수/영/탐 중 택2
    df_result.loc[df_result['산출번호'] == 37, '환산점수'] = df_result[['수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1) + plus_ect - \
                                                     df_result[['수학환산점수', '영어환산점수', '탐구환산점수']].min(axis=1)
    # 국/영/탐 중 택2
    df_result.loc[df_result['산출번호'] == 38, '환산점수'] = df_result[['국어환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1) + plus_ect - \
                                                     df_result[['국어환산점수', '영어환산점수', '탐구환산점수']].min(axis=1)
    # 탐+국/수/영 중 택2
    df_result.loc[df_result['산출번호'] == 39, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1) \
                                                     + plus_ect - df_result[['국어환산점수', '수학환산점수', '영어환산점수']].min(axis=1)
    # 탐+국/수/영 중 택1
    df_result.loc[df_result['산출번호'] == 40, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수']].max(axis=1) + plus_ect + df_result['탐구환산점수']
    # 탐+국/수 중 택1
    df_result.loc[df_result['산출번호'] == 41, '환산점수'] = df_result[['국어환산점수', '수학환산점수']].max(axis=1) + plus_ect + df_result['탐구환산점수']
    # 탐+국/영 중 택1
    df_result.loc[df_result['산출번호'] == 42, '환산점수'] = df_result[['국어환산점수', '영어환산점수']].max(axis=1) + plus_ect + df_result['탐구환산점수']
    # 탐+수/영 중 택1
    df_result.loc[df_result['산출번호'] == 43, '환산점수'] = df_result[['수학환산점수', '영어환산점수']].max(axis=1) + plus_ect + df_result['탐구환산점수']

    # ★★★★★★★별도산출: 경남대 25201
    # code 1: 영역선택시 가산점 제외하고 상위 3개 영역 선택, 수학이 선택되지 않아도 미적분or기하 응시한 경우 무조건 총점에 가산점 합산
    df_result.loc[(df_result['대학코드'] == 25201) & (df_result['수능별도산출코드'] == 1), '환산점수'] = df_result[['국어환산점수', '수학가산전', '영어환산점수', '탐구환산점수']].sum(axis=1) - \
                                                        df_result[['국어환산점수', '수학가산전', '영어환산점수', '탐구환산점수']].min(axis=1) + \
                                                        df_result['수학가산점'].fillna(0) + plus_ect
    # ☆☆☆☆☆☆☆ 경남대 별도산출 영역 종료

    # ★★★★★★★별도산출: 경동대 14202
    # code 1: 수능 평균등급을 계산 후 해당 구간의 등급점수 부여
    u_14202_avr = round((guk_dsc + su_dsc + eng_dsc + min(tam1_dsc, tam2_dsc)) / 4, 2)
    if u_14202_avr < 2:
        u_14202_dsc = 1
    elif u_14202_avr >= 2 and u_14202_avr < 3:
        u_14202_dsc = 2
    elif u_14202_avr >= 3 and u_14202_avr < 4:
        u_14202_dsc = 3
    elif u_14202_avr >= 4 and u_14202_avr < 5:
        u_14202_dsc = 4
    elif u_14202_avr >= 5 and u_14202_avr < 6:
        u_14202_dsc = 5
    elif u_14202_avr >= 6 and u_14202_avr < 7:
        u_14202_dsc = 6
    elif u_14202_avr >= 7 and u_14202_avr < 8:
        u_14202_dsc = 7
    elif u_14202_avr >= 8 and u_14202_avr < 9:
        u_14202_dsc = 8
    else:
        u_14202_dsc = 9
    df_result.loc[df_result['대학코드'] == 14202, '환산점수'] = df_dguk.iloc[:, u_14202_dsc - 1] + plus_ect
    # ☆☆☆☆☆☆☆ 경동대 별도산출 영역 종료

    # ★★★★★★★별도산출: 고려대(세종) 17202 (2/2)
    # code 1 국영+수/탐2 조합 케이스
    su_type17202 = df['수능만점'] * (df['국어원점'] * df['국어영역만점'] + df['영어환산점수'] * df['영어영역만점'] + df['수학원점'] * df['수학영역만점']) \
                   / (top_scr_guk * df['국어영역만점'] + top_scr_su * df['수학영역만점'] + 100 * df['영어영역만점'])
    tam_type17202 = df['수능만점'] * (df['국어원점'] * df['국어영역만점'] + df['영어환산점수'] * df['영어영역만점'] + (df['탐1원점'] + df['탐2원점']) * df['탐구영역만점']) \
                    / (top_scr_guk * df['국어영역만점'] + 100 * df['영어영역만점'] + (df['탐1표점최고'] + df['탐2표점최고']) * df['탐구영역만점'])
    select_17202 = pd.concat([su_type17202, tam_type17202], axis=1)
    df_result.loc[(df['대학코드'] == 17202) & (df['수능조합'] == '국영+수/탐2'), '환산점수'] = select_17202.max(axis=1)
    # ☆☆☆☆☆☆☆ 고려대(세종) 별도산출 (2/2) 영역 종료

    # ★★★★★★★별도산출: 대진대 13205
    # code 1
    # 1. 국,영,수 중 1개 영역 선택
    # 2. 1에서 선택되지 않은 1개 영역과 탐구1,2,한국사 영역 중 백분위가 높은 1개 영역을 선택함
    # 3. 1에서 선택된 1개 영역은 60% 반영, 2에서 선택된 1개 영역은 40% 반영한다.
    df.loc[(df['대학코드'] == 13205) & (df['수능별도산출코드'] == 1), '탐평가산원점'] = df[['탐1가산원점', '탐2가산원점', '한국사']].max(axis=1)
    score_rank13205 = df[['국어원점', '수학가산원점', '영어', '탐평가산원점']].rank(axis=1, method='min', na_option='bottom', ascending=False)
    score_rank13205['국'] = score_rank13205['국어원점'] + 0.2
    score_rank13205['수'] = score_rank13205['수학가산원점'] + 0
    score_rank13205['영'] = score_rank13205['영어'] + 0.3
    score_rank13205['탐'] = score_rank13205['탐평가산원점'] + 0.1
    df_score_rank13205 = score_rank13205[['국', '수', '영', '탐']].rank(axis=1, method='min', na_option='bottom', ascending=True)
    df_result.loc[((df_score_rank13205['국'] == 3) | (df_score_rank13205['국'] == 4)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 0
    df_result.loc[((df_score_rank13205['수'] == 3) | (df_score_rank13205['수'] == 4)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 0
    df_result.loc[((df_score_rank13205['영'] == 3) | (df_score_rank13205['영'] == 4)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 0
    df_result.loc[((df_score_rank13205['탐'] == 3) | (df_score_rank13205['탐'] == 4)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '탐구영역만점'] = 0
    df_result.loc[((df_score_rank13205['탐'] == 1) | (df_score_rank13205['탐'] == 2)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '탐구영역만점'] = 400
    df_result.loc[(df_score_rank13205['국'] == 1) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 600
    df_result.loc[(df_score_rank13205['수'] == 1) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 600
    df_result.loc[(df_score_rank13205['영'] == 1) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 600
    df_result.loc[((df_score_rank13205['탐'] == 1) & (df_score_rank13205['국'] == 2)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 600
    df_result.loc[((df_score_rank13205['탐'] == 1) & (df_score_rank13205['수'] == 2)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 600
    df_result.loc[((df_score_rank13205['탐'] == 1) & (df_score_rank13205['영'] == 2)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 600
    df_result.loc[((df_score_rank13205['탐'] != 1) & (df_score_rank13205['국'] == 2)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 400
    df_result.loc[((df_score_rank13205['탐'] != 1) & (df_score_rank13205['수'] == 2)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 400
    df_result.loc[((df_score_rank13205['탐'] != 1) & (df_score_rank13205['영'] == 2)) & (df['대학코드'] == 13205) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 400
    df_result.loc[(df['대학코드'] == 13205) & (df['수능별도산출코드'] == 1), '국어환산점수'] = df_result['국어영역만점'] * df['국어원점'] * 0.01
    df_result.loc[(df['대학코드'] == 13205) & (df['수능별도산출코드'] == 1), '수학환산점수'] = df_result['수학영역만점'] * df['수학가산원점'] * 0.01
    df_result.loc[(df['대학코드'] == 13205) & (df['수능별도산출코드'] == 1), '영어환산점수'] = df_result['영어영역만점'] * df['영어'] * 0.01
    df_result.loc[(df['대학코드'] == 13205) & (df['수능별도산출코드'] == 1), '탐구환산점수'] = df_result['탐구영역만점'] * df['탐평가산원점'] * 0.01
    # 수능 합계 계산
    df_result.loc[(df['대학코드'] == 13205) & (df['수능별도산출코드'] == 1), '환산점수'] \
        = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1)
    # ☆☆☆☆☆☆☆ 대진대 별도산출 영역 종료

    # ★★★★★★★별도산출: 목원대 16203
    # code 1: 국어,수학,영어,탐구1,탐구2,한국사 총 6개 영역 중 백분위가 제일 높은 영역에 300점, 2등으로 높은 영역에 200점 부여
    score_rank16203 = df[['국어원점', '수학가산원점', '영어', '탐1가산원점', '탐2가산원점', '한국사']].rank(axis=1, method='min',
                                                                                   na_option='bottom', ascending=False)
    score_rank16203['국'] = score_rank16203['국어원점'] + 0.2
    score_rank16203['수'] = score_rank16203['수학가산원점'] + 0
    score_rank16203['영'] = score_rank16203['영어'] + 0.3
    score_rank16203['탐1'] = score_rank16203['탐1가산원점'] + 0.1
    score_rank16203['탐2'] = score_rank16203['탐2가산원점'] + 0.15
    score_rank16203['한'] = score_rank16203['한국사'] + 0.4
    df_score_rank16203 = score_rank16203[['국', '수', '영', '탐1', '탐2', '한']].rank(axis=1, method='min',
                                                                                na_option='bottom')
    df_result.loc[
        (df_score_rank16203['국'] == 1) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '국어환산점수'] = \
    df_result['국어원점'] * 6
    df_result.loc[
        (df_score_rank16203['국'] == 2) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '국어환산점수'] = \
    df_result['국어원점'] * 4
    df_result.loc[(df_score_rank16203['국'] != 1) & (df_score_rank16203['국'] != 2) & (df_result['대학코드'] == 16203) & (
                df_result['수능별도산출코드'] == 1), '국어환산점수'] = 0
    df_result.loc[
        (df_score_rank16203['수'] == 1) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '수학환산점수'] = \
    df_result['수학원점'] * 6
    df_result.loc[
        (df_score_rank16203['수'] == 2) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '수학환산점수'] = \
    df_result['수학원점'] * 4
    df_result.loc[(df_score_rank16203['수'] != 1) & (df_score_rank16203['수'] != 2) & (df_result['대학코드'] == 16203) & (
                df_result['수능별도산출코드'] == 1), '수학환산점수'] = 0
    df_result.loc[
        (df_score_rank16203['영'] == 1) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '영어환산점수'] = \
    df_result['영어'] * 6
    df_result.loc[
        (df_score_rank16203['영'] == 2) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '영어환산점수'] = \
    df_result['영어'] * 4
    df_result.loc[(df_score_rank16203['영'] != 1) & (df_score_rank16203['영'] != 2) & (df_result['대학코드'] == 16203) & (
                df_result['수능별도산출코드'] == 1), '영어환산점수'] = 0
    df_result.loc[
        (df_score_rank16203['탐1'] == 1) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '탐1환산점수'] = \
    df_result['탐1원점'] * 6
    df_result.loc[
        (df_score_rank16203['탐1'] == 2) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '탐1환산점수'] = \
    df_result['탐1원점'] * 4
    df_result.loc[(df_score_rank16203['탐1'] != 1) & (df_score_rank16203['탐1'] != 2) & (df_result['대학코드'] == 16203) & (
                df_result['수능별도산출코드'] == 1), '탐1환산점수'] = 0
    df_result.loc[
        (df_score_rank16203['탐2'] == 1) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '탐2환산점수'] = \
    df_result['탐2원점'] * 6
    df_result.loc[
        (df_score_rank16203['탐2'] == 2) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '탐2환산점수'] = \
    df_result['탐2원점'] * 4
    df_result.loc[(df_score_rank16203['탐2'] != 1) & (df_score_rank16203['탐2'] != 2) & (df_result['대학코드'] == 16203) & (
                df_result['수능별도산출코드'] == 1), '탐2환산점수'] = 0
    df_result.loc[
        (df_score_rank16203['한'] == 1) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '한국사환산점수'] = \
    df_result['한국사'] * 6
    df_result.loc[
        (df_score_rank16203['한'] == 2) & (df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '한국사환산점수'] = \
    df_result['한국사'] * 4
    df_result.loc[(df_score_rank16203['한'] != 1) & (df_score_rank16203['한'] != 2) & (df_result['대학코드'] == 16203) & (
                df_result['수능별도산출코드'] == 1), '한국사환산점수'] = 0
    df_result.loc[(df_result['대학코드'] == 16203) & (df_result['수능별도산출코드'] == 1), '환산점수'] = df_result[
        ['국어환산점수', '수학환산점수', '영어환산점수', '탐1환산점수', '탐2환산점수', '한국사환산점수']].sum(axis=1)
    # ☆☆☆☆☆☆☆ 목원대 별도산출 영역 종료

    # ★★★★★★★별도산출: 서울대 111102
    # code 1 제2외 등급에 따른 감산이 존재하나 응시자가 기하or미적분 and 과탐2개(I + II)를 응시한 경우, 제2외 응시 필수 아님. 응시 했어도 제2외 가산점 반영 안함
    # code 2 1단계 합격자 최고점과 최저점을 사용하여 응시자 점수 표준화
    # 서울대 전 모집단위는 최종 계산 시 소수점 셋째자리 이하를 버림 처리한다. (23학년도 삭제)
    if (su_select == '미적분' or su_select == '기하') and user_tam1_type == '과탐' and user_tam2_type == '과탐':
        df_result.loc[(df_result['대학코드'] == 11102) & (df_result['수능별도산출코드'] == 1), '제2외환산점수'] = 0
    #df_result.loc[df_result['대학코드'] == 11102, '환산점수'] \
    #    = (100 * df_result[['국어환산점수', '수학가산전', '영어환산점수', '탐구환산점수', '한국사환산점수', '제2외환산점수']].sum(axis=1)).apply(np.floor) / 100
    # ☆☆☆☆☆☆☆ 서울대 별도산출 영역 종료

    # ★★★★★★★별도산출: 신한대 13214
    # code 1 국/수 중 1개 영역 선택 + 영/탐1/한 중 1개 영역 선택 (총 2개 영역 반영)
    # code 2 탐1 필수 + 국/수 중 1개 영역 선택 + 영/한 중 1개 영역 선택 (총 3개 영역 반영)
    df_result.loc[(df_result['대학코드'] == 13214) & (df_result['수능별도산출코드'] == 1), '환산점수'] \
        = df_result[['국어환산점수', '수학환산점수']].max(axis=1) + df_result[['영어환산점수', '한국사', '탐구환산점수']].max(axis=1)
    df_result.loc[(df_result['대학코드'] == 13214) & (df_result['수능별도산출코드'] == 2), '환산점수'] \
        = df_result['탐구환산점수'] + df_result[['국어환산점수', '수학환산점수']].max(axis=1) + df_result[['영어환산점수', '한국사']].max(axis=1)
    # ☆☆☆☆☆☆☆ 신한대 별도산출 영역 종료

    # ★★★★★★★별도산출: 이화여대 11227
    # code 1 자연계열 수학/탐구 조건(기하or미적분 and 과탐응시)을 충족하는 응시자에 한해 인문 산출(A) 방식과 자연 산출(B) 방식 중 점수가 더 높은쪽으로 채택
    ehwa_inmun = float(df_result['환산점수'].loc[df_result['모집요강코드'] == 112271013])  # 의예인문 모집단위코드
    ehwa_jayeon = float(df_result['환산점수'].loc[df_result['모집요강코드'] == 112272025])  # 의예자연 모집단위코드
    if (su_select == '미적분' or su_select == '기하') and user_tam1_type == '과탐' and user_tam2_type == '과탐':
        ehwa_gongtong = max(ehwa_inmun, ehwa_jayeon)
    else:
        ehwa_gongtong = ehwa_inmun
    df_result.loc[(df_result['대학코드'] == 11227) & (df_result['수능별도산출코드'] == 1), '환산점수'] = ehwa_gongtong
    # ☆☆☆☆☆☆☆ 이화여대 별도산출 영역 종료

    # ★★★★★★★별도산출: 유원대 15206
    # code 1 국어, 수학, 영어, 탐구, 한국사에 각각 등급점수 부여 후 등급점수가 높은 4개 영역의 점수를 합산한다.
    df_result.loc[(df_result['대학코드'] == 15206) & (df_result['수능별도산출코드'] == 1), '환산점수'] \
            = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수', '한국사']].sum(axis=1) \
            - df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수', '한국사']].min(axis=1)
    # ☆☆☆☆☆☆☆ 유원대 별도산출 영역 종료

    # ★★★★★★★별도산출: 청운대 17401
    # code 1
    # 1. 국,영,수 중 2개 영역 선택
    # 2. 1에서 선택되지 않은 1개 영역과 탐구 영역 중 백분위가 높은 1개 영역을 선택함
    # 3. 1에서 선택된 2개 영역은 각각 40% 반영, 2에서 선택된 1개 영역은 20% 반영한다.
    df_result.loc[(df_result['대학코드'] == 17401) & (df_result['수능별도산출코드'] == 1), '수학환산점수'] = 2 * (
                df_result[['국어원점', '수학가산원점', '영어']].sum(axis=1) - df_result[['국어원점', '수학가산원점', '영어']].min(axis=1))
    select1_17401 = pd.DataFrame(df_result[['국어원점', '수학가산원점', '영어']].min(axis=1))
    select2_17401 = pd.DataFrame(df_result[['탐1원점', '탐2원점', '제2외']].max(axis=1))
    select_17401 = pd.concat([select1_17401, select2_17401], axis=1)
    df_result.loc[(df_result['대학코드'] == 17401) & (df_result['수능별도산출코드'] == 1), '탐구환산점수'] = select_17401.max(axis=1)
    df_result.loc[(df_result['대학코드'] == 17401) & (df_result['수능별도산출코드'] == 1), '환산점수'] \
        = df_result['수학환산점수'] + df_result['탐구환산점수']
    # ☆☆☆☆☆☆☆ 청운대 별도산출 영역 종료

    # ★★★★★★★별도산출: 청주대 15208 (2/2)
    # 공통 영역 선택 시 가산점 미반영 상태에서 선택, 따라서 선택되지 않는 경우 가산점도 미반영
    # code 1: 수학은 가산점을 더해도 영역만점을 넘을 수 없음, 수학 미 채택 시 가산점 반영 없음
    # code 2: code1 + 탐구 2개 영역 모두 과탐을 응시한 경우에 한해 원점기준 10점의 가산점을 최종 합산 시에 부여 (즉, 탐구는 영역만점 초과 가능) 탐구 미 채택 시 가산점 반영도 없음 (영역의 선택은 가산점 미포함 기준으로 선택하며, 가산전 환산점수로 영역을 선택할 때 동점이 존재하는 경우 1.수학 2.탐구 3.국어 4.영어 순으로 뽑는다.)
    # code 3: 수학은 가산점을 더해도 영역만점을 넘을 수 없음, 과탐은 가산점을 최종시점에 총점에 합산하므로 영역만점 초과 가능
    # 국/수/영/탐(2) 4개 영역 중 원점기준 4위인 항목은 영역만점 0으로 처리
    df_result.loc[(df_rank['국어rank'] == 4) & (df_result['대학코드'] == 15208) & (
                (df_result['수능별도산출코드'] == 1) | (df_result['수능별도산출코드'] == 2)), '국어환산점수'] = 0
    df_result.loc[(df_rank['수학rank'] == 4) & (df_result['대학코드'] == 15208) & (
                (df_result['수능별도산출코드'] == 1) | (df_result['수능별도산출코드'] == 2)), '수학환산점수'] = 0
    df_result.loc[(df_rank['영어rank'] == 4) & (df_result['대학코드'] == 15208) & (
                (df_result['수능별도산출코드'] == 1) | (df_result['수능별도산출코드'] == 2)), '영어환산점수'] = 0
    df_result.loc[(df_rank['탐구rank'] == 4) & (df_result['대학코드'] == 15208) & (
                (df_result['수능별도산출코드'] == 1) | (df_result['수능별도산출코드'] == 2)), '탐구환산점수'] = 0
    # 가산점을 포함한 수학 환산 점수가 영역만점을 넘을 경우 영역만점으로 반영한다.
    df_result.loc[(df_result['대학코드'] == 15208) & (df_result['수학환산점수'] > df_result['수학영역만점']), '수학환산점수'] = df_result['수학영역만점']
    df_result.loc[df_result['대학코드'] == 15208, '환산점수'] = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1)
    # ☆☆☆☆☆☆☆ 청주대 별도산출 영역 (2/2) 종료

    # ★★★★★★★별도산출: 평택대 13222
    # code 1 : 국수영탐 중 백분위점수(가산점 포함)가 우수한 순서대로 3개 영역을 선택하여 영역만점을 350, 350, 300점씩 반영한다. 수학, 과탐과 같이 가산점이 있는 영역은 가산점을 부여 한 후 순위를 정한다.
    df_result.loc[(df_rank['국어rank'] == 3) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '국어환산점수'] = \
    df['국어환산점수'] * 3 / 3.5
    df_result.loc[(df_rank['수학rank'] == 3) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '수학환산점수'] = \
    df['수학환산점수'] * 3 / 3.5
    df_result.loc[(df_rank['영어rank'] == 3) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '영어환산점수'] = \
    df['영어환산점수'] * 3 / 3.5
    df_result.loc[(df_rank['탐구rank'] == 3) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '탐구환산점수'] = \
    df['탐구환산점수'] * 3 / 3.5
    df_result.loc[(df_rank['국어rank'] == 4) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '국어환산점수'] = 0
    df_result.loc[(df_rank['수학rank'] == 4) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '수학환산점수'] = 0
    df_result.loc[(df_rank['영어rank'] == 4) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '영어환산점수'] = 0
    df_result.loc[(df_rank['탐구rank'] == 4) & (df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '탐구환산점수'] = 0
    df_result.loc[(df_result['대학코드'] == 13222) & (df_result['수능별도산출코드'] == 1), '환산점수'] = df_result[
        ['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1)
    # ☆☆☆☆☆☆☆ 평택대 별도산출 영역 종료

    # ★★★★★★★별도산출: 한국항공대 13225
    # code 1 수능 환산점수 합산 시 소수점 첫째자리에서 반올림 후 정수 처리
    df_result.loc[(df_result['대학코드'] == 13225) & (df_result['수능별도산출코드'] == 1), '환산점수'] = df_result['환산점수'].round(0)
    # ☆☆☆☆☆☆☆ 한국항공대 별도산출 영역 종료

    # ★★★★★★★별도산출: 한림대 14206
    # code 1: 과탐II 과목 중 하나를 응시한 경우 7% 가산, 과탐I 과목 중 하나를 응시한 경우 5% 가산 (환산기준)
    if user_tam1_type == '과탐':
        if tam1_select[-1:] == '2':
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 1), '탐1가산원점'] = df['탐1원점'] * 1.07
        else:
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 1), '탐1가산원점'] = df['탐1원점'] * 1.05
    else:
        df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 1), '탐1가산원점'] = df['탐1원점']
    if user_tam2_type == '과탐':
        if tam2_select[-1:] == '2':
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 1), '탐2가산원점'] = df['탐2원점'] * 1.07
        else:
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 1), '탐2가산원점'] = df['탐2원점'] * 1.05
    else:
        df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 1), '탐2가산원점'] = df['탐2원점']

    # code 2: 과탐II 과목 중 하나를 응시한 경우 15% 가산, 과탐I 과목 중 하나를 응시한 경우 10% 가산 (환산기준)
    if user_tam1_type == '과탐':
        if tam1_select[-1:] == '2':
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 2), '탐1가산원점'] = df['탐1원점'] * 1.15
        else:
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 2), '탐1가산원점'] = df['탐1원점'] * 1.1
    else:
        df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 2), '탐1가산원점'] = df['탐1원점']
    if user_tam2_type == '과탐':
        if tam2_select[-1:] == '2':
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 2), '탐2가산원점'] = df['탐2원점'] * 1.15
        else:
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 2), '탐2가산원점'] = df['탐2원점'] * 1.1
    else:
        df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 2), '탐2가산원점'] = df['탐2원점']

    # code 3: 지구과학1,2 중 하나를 응시한 경우 10% 가산, 그 외 과탐 과목 중 하나를 응시한 경우 15% 가산 (환산기준)
    if user_tam1_type == '과탐':
        if tam1_select[:2] == '지구':
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 3), '탐1가산원점'] = df['탐1원점'] * 1.1
        else:
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 3), '탐1가산원점'] = df['탐1원점'] * 1.15
    else:
        df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 3), '탐1가산원점'] = df['탐1원점']

    if user_tam2_type == '과탐':
        if tam2_select[:2] == '지구':
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 3), '탐2가산원점'] = df['탐2원점'] * 1.1
        else:
            df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 3), '탐2가산원점'] = df['탐2원점'] * 1.15
    else:
        df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 3), '탐2가산원점'] = df['탐2원점']

    # code 1,2,9 국/영/수 중 최고점 1개 선택 700점 부여 후, 선택된 영역을 제외한 나머지 두 영역과 탐구(2과목평균) 중 한 영역을 선택하여 300점 반영(가산포함하여 선택, 동점일 때는 랜덤 선택)
    df.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'].notnull()), '탐평가산원점'] = df[['탐1가산원점', '탐2가산원점']].sum(axis=1) * 0.5
    score_rank14206 = df[['국어원점', '수학가산원점', '영어', '탐평가산원점']].rank(axis=1, method='min', na_option='bottom', ascending=False)
    score_rank14206['국'] = score_rank14206['국어원점'] + 0.2
    score_rank14206['수'] = score_rank14206['수학가산원점'] + 0
    score_rank14206['영'] = score_rank14206['영어'] + 0.3
    score_rank14206['탐'] = score_rank14206['탐평가산원점'] + 0.1
    df_score_rank14206 = score_rank14206[['국', '수', '영', '탐']].rank(axis=1, method='min', na_option='bottom', ascending=True)
    df_result.loc[((df_score_rank14206['국'] == 3) | (df_score_rank14206['국'] == 4)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 0
    df_result.loc[((df_score_rank14206['수'] == 3) | (df_score_rank14206['수'] == 4)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 0
    df_result.loc[((df_score_rank14206['영'] == 3) | (df_score_rank14206['영'] == 4)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 0
    df_result.loc[((df_score_rank14206['탐'] == 3) | (df_score_rank14206['탐'] == 4)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '탐구영역만점'] = 0
    df_result.loc[((df_score_rank14206['탐'] == 1) | (df_score_rank14206['탐'] == 2)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '탐구영역만점'] = 300
    df_result.loc[(df_score_rank14206['국'] == 1) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 700
    df_result.loc[(df_score_rank14206['수'] == 1) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 700
    df_result.loc[(df_score_rank14206['영'] == 1) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 700
    df_result.loc[((df_score_rank14206['탐'] == 1) & (df_score_rank14206['국'] == 2)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 700
    df_result.loc[((df_score_rank14206['탐'] == 1) & (df_score_rank14206['수'] == 2)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 700
    df_result.loc[((df_score_rank14206['탐'] == 1) & (df_score_rank14206['영'] == 2)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 700
    df_result.loc[((df_score_rank14206['탐'] != 1) & (df_score_rank14206['국'] == 2)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '국어영역만점'] = 300
    df_result.loc[((df_score_rank14206['탐'] != 1) & (df_score_rank14206['수'] == 2)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '수학영역만점'] = 300
    df_result.loc[((df_score_rank14206['탐'] != 1) & (df_score_rank14206['영'] == 2)) & (df['대학코드'] == 14206) & (
                (df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어영역만점'] = 300
    df_result.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'].notnull()), '국어환산점수'] = df_result['국어영역만점'] * df[
        '국어원점'] * 0.01
    df_result.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'].notnull()), '수학환산점수'] = df_result['수학영역만점'] * df[
        '수학가산원점'] * 0.01
    df_result.loc[
        (df['대학코드'] == 14206) & ((df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '영어환산점수'] = \
    df_result['영어영역만점'] * df['영어'] * 0.01
    df_result.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'].notnull()), '탐구환산점수'] = df_result['탐구영역만점'] * df[
        '탐평가산원점'] * 0.01
    # 전체: 가산점을 포함한 점수가 영역만점을 넘을 경우 영역만점으로 반영한다.
    df_result.loc[(df['대학코드'] == 14206) & (df_result['수학환산점수'] > df_result['수학영역만점']), '수학환산점수'] = df_result['수학영역만점']
    df_result.loc[(df['대학코드'] == 14206) & (df_result['탐구환산점수'] > df_result['탐구영역만점']), '탐구환산점수'] = df_result['탐구영역만점']
    # 수능 합계 계산
    df_result.loc[(df['대학코드'] == 14206) & ((df['수능별도산출코드'] == 1) | (df['수능별도산출코드'] == 2) | (df['수능별도산출코드'] == 9)), '환산점수'] \
    = df_result[['국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수']].sum(axis=1)
    df_result.loc[(df['대학코드'] == 14206) & (df['수능별도산출코드'] == 3), '환산점수'] \
        = df_result['수학환산점수'] + df_result['영어환산점수'] + df_result[['국어환산점수', '탐구환산점수']].max(axis=1)
    # ☆☆☆☆☆☆☆ 한림대 별도산출 영역 종료

    #common024 최종 산출 완료 df
    # df_common = df_result[['모집요강코드', '대학명', '학과명', '사정모형', '수능별도산출코드', '변환표준공식번호', '수능활용점수', '환산점수', \
    #                        '국어환산점수', '수학환산점수', '영어환산점수', '탐구환산점수', '한국사환산점수', '제2외환산점수', \
    #                        '수학가산전', '수학가산점', '탐1가산전', '탐1가산점', '탐2가산전', '탐2가산점']]
    df_common = df_result[['대학명', '학과명', '군', '계열', '인원', '수능활용', '수학선택', '탐구선택', '수능조합', '환산점수', '커트라인']]
    # df_common['대학'] = df_common['대학명'] + " " + df_common['학과명']
    # df_final = df_common[['대학', '수능활용점수', '환산점수']]
    #df_common = df_result
    return df_common

