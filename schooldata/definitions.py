SCHOOL_FIELD_MAP = {
    'SCH_ADDRESS1': 'school_address_1',
    'SCH_ADDRESS2': 'school_address_2',
    'SCH_ADDRESS3': 'school_address_3',
    'SCH_NFTYPE': 'school_type',
    'SCH_POSTCODE':'postcode',
    'SCH_SCHOOLNAME': 'name',
    'SCH_TOWN':'town',
    'KS4_URN': 'urn'
}

PUPIL_FIELD_MAP = {
    bool : [
        'ABS_PersistentAbsentee15_3Term',
        'ABS_PersistentAbsentee_3Term',
        'CEN_FSMEligible',
        'KS4_ENTRY_5', # entered for at least 5 GCSE/equivs
        'KS4_ALLSCI', # entered all sciences
        'KS4_FIVEAC',
        'KS4_FIVEAG',
        'KS4_ANYLEV1',
        'KS4_LEVEL2_EM',    # 5 or more including EM, including equivs
        'KS4_LEVEL2EM_GCSE',# 5 or more including EM, EXCLUDING equivs
        'KS4_GCSE_MATHATT', # attempted maths
        'KS4_GCSE_SCIATT',
        'KS4_GCSE_ENGATT',
    ],
    int : [
        'ABS_AuthorisedAbsence_3Term',
        'ABS_OverallAbsence_3Term',
        'ABS_SessionsPossible_3Term',
        'ABS_UnauthorisedAbsence_3Term',

        'CEN_AgeAtStartOfAcademicYear',

        'EXC_PermanentExclusionCount',
        'EXC_TotalFixedExclusions',
        'EXC_TotalFixedSessions',

        'KS4_ENTRY_E', # total number of gcse and equiv entries
        'KS4_GCSE_AA',
        'KS4_GCSE_AC',
        'KS4_GCSE_AG',
        'KS4_GCSE_DG',
        'KS4_GCSE_E',
        'KS4_PASS_AC_AAT', # num passes at grades a-c, eqivals included
        'KS4_PASS_AG', # total qualifications, a* - g
        'KS4_KS4SCI',

        'KS4_KS2ENG24P', # english prior attainment
        'KS4_KS2MAT24P', # maths prior attainment
        'KS4_Flag24ENGPrg', # achieved expected KS2->KS4 eng progress
        'KS4_Flag24MATPrg', # math progress

    ],
    float : [
        'KS4_GPTSPE', # points per entry including equivs
    ],
    str: [
        'KS4_RECORDID',
        'CEN_EthnicGroupMinor',
        'CEN_LSOA',
        'CEN_LanguageGroupMinor',

        'KS2_CVAAPS', # KS2 average point score
        'KS2_ENGLEV', # 
        'KS2_MATLEV',
        'KS2_SCILEV',
        'KS2_TOTPTS',

        'KS4_GENDER',
        'KS4_LA',   #local auth
        'KS4_TOE_CODE', # type of extablishment
        'KS4_HGMATH', # highest grade maths ('A-G')
        'CEN_SENProvision',
    ]
}

