# --- Αρχείο: part2_bhma1_teacher_children_full (2).py ---

import random

def is_conflict(student_row, section_students, df):
    """Έλεγχος αν υπάρχει σύγκρουση με κάποιον μαθητή στο ίδιο τμήμα"""
    conflicts = str(student_row['ΣΥΓΚΡΟΥΣΕΙΣ']).replace(' ', '').split(',')
    for name in section_students:
        if name in conflicts:
            return True
    return False

def is_mutual_friend(df, student_name, other_name):
    """Έλεγχος πλήρως αμοιβαίας φιλίας"""
    s1_friends = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == student_name, 'ΦΙΛΙΑ'].values[0]).replace(' ', '').split(',')
    s2_friends = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == other_name, 'ΦΙΛΙΑ'].values[0]).replace(' ', '').split(',')
    return student_name in s2_friends and other_name in s1_friends

def assign_teacher_children(df, num_sections):
    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = df.get('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ', '')
    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].astype(str)
    df['ΤΜΗΜΑ'] = df.get('ΤΜΗΜΑ', '')
    
    teacher_children = df[(df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν') & (df['ΤΜΗΜΑ'] == '')]

    sections = {i+1: [] for i in range(num_sections)}

    if len(teacher_children) <= num_sections:
        for i, (_, row) in enumerate(teacher_children.iterrows()):
            section_number = i + 1
            df.at[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = f'Τμήμα {section_number}'
            sections[section_number].append(row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'])
    else:
        for _, row in teacher_children.iterrows():
            student_name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
            gender = row['ΦΥΛΟ']
            placed = False

            candidate_sections = sorted(sections.items(), key=lambda x: len(x[1]))
            
            for sec, students in candidate_sections:
                if is_conflict(row, students, df):
                    continue

                friend_names = str(row['ΦΙΛΙΑ']).replace(' ', '').split(',')
                if any(friend in students and is_mutual_friend(df, student_name, friend) for friend in friend_names if friend):
                    df.at[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = f'Τμήμα {sec}'
                    sections[sec].append(student_name)
                    placed = True
                    break

            if not placed:
                for sec, students in candidate_sections:
                    same_gender_count = sum(1 for name in students if df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΦΥΛΟ'].values[0] == gender)
                    other_gender_count = len(students) - same_gender_count
                    if other_gender_count < same_gender_count:
                        df.at[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = f'Τμήμα {sec}'
                        sections[sec].append(student_name)
                        placed = True
                        break

            if not placed:
                sec = candidate_sections[0][0]
                df.at[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = f'Τμήμα {sec}'
                sections[sec].append(student_name)

    return df


# --- Αρχείο: part2_bhma2_lively_students.py ---

def assign_lively_students(df, num_classes):
    lively_students = df[(df['ΖΩΗΡΟΣ'] == 'Ν') & (df['ΤΜΗΜΑ'].isna())]
    proposed = df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].copy()

    # Αρχικοποίηση μετρητών ζωηρών ανά τμήμα
    lively_per_class = {i: 0 for i in range(1, num_classes + 1)}
    for _, row in df[df['ΖΩΗΡΟΣ'] == 'Ν'].iterrows():
        assigned = row.get('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ') or row.get('ΤΜΗΜΑ')
        if pd.notna(assigned):
            lively_per_class[int(assigned)] += 1

    # Συνάρτηση υπολογισμού υποψήφιου τμήματος για κάθε ζωηρό μαθητή
    def find_best_class(student_name, gender, conflicts, friend, friend_section):
        # Προτεραιότητα 1: Φιλία με παιδί εκπαιδευτικού
        if pd.notna(friend) and pd.notna(friend_section):
            if lively_per_class[int(friend_section)] < 1 and friend not in conflicts:
                return int(friend_section)

        # Εύρεση τμήματος με 0 ζωηρούς
        for section, count in lively_per_class.items():
            if count == 0:
                # Αποφυγή σύγκρουσης και ομοιομορφίας φύλου
                section_students = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == section]
                if student_name not in section_students['ΣΥΓΚΡΟΥΣΕΙΣ'].fillna('').str.split(',').sum():
                    if gender == 'Α' and 'Α' not in section_students['ΦΥΛΟ'].values:
                        return section
                    elif gender == 'Κ' and 'Κ' not in section_students['ΦΥΛΟ'].values:
                        return section
                    elif len(section_students) == 0:
                        return section

        # Αν δεν βρέθηκε, τότε στο πιο ελαφρύ
        min_lively = min(lively_per_class.values())
        for section, count in lively_per_class.items():
            if count == min_lively:
                return section

        return None

    # Κατανομή ζωηρών μαθητών
    for _, row in lively_students.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        gender = row['ΦΥΛΟ']
        conflicts = str(row.get('ΣΥΓΚΡΟΥΣΕΙΣ', '')).replace(' ', '').split(',') if pd.notna(row.get('ΣΥΓΚΡΟΥΣΕΙΣ')) else []

        # Εύρεση φίλου εκπαιδευτικού (αν υπάρχει)
        friends = str(row.get('ΦΙΛΟΙ', '')).replace(' ', '').split(',')
        mutual_friend = None
        mutual_friend_section = None
        for friend in friends:
            if is_mutual_friend(df, name, friend):
                friend_row = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == friend]
                if not friend_row.empty and friend_row.iloc[0]['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν':
                    mutual_friend = friend
                    mutual_friend_section = friend_row.iloc[0].get('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ')
                    break

        best_class = find_best_class(name, gender, conflicts, mutual_friend, mutual_friend_section)
        if best_class:
            proposed.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name] = best_class
            lively_per_class[best_class] += 1

    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = proposed
    return df


# --- Αρχείο: part3_bhma3_special_students.py ---

# Βήμα 3 – Κατανομή Παιδιών με Ιδιαιτερότητες
def assign_special_needs_students(df, num_classes):
    df = df.copy()
    special_counts = {f"Τμήμα {i+1}": 0 for i in range(num_classes)}
    lively_counts = {f"Τμήμα {i+1}": 0 for i in range(num_classes)}

    for idx, row in df.iterrows():
        section = row['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']
        if pd.notna(section):
            if row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν':
                special_counts[section] += 1
            if row['ΖΩΗΡΟΣ'] == 'Ν':
                lively_counts[section] += 1

    special_students = df[(df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].isna())]

    for idx, student in special_students.iterrows():
        conflicts = str(student['ΣΥΓΚΡΟΥΣΕΙΣ']).replace(" ", "").split(',')
        gender = student['ΦΥΛΟ']
        name = student['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        limit_one_per_class = len(special_students) <= num_classes

        best_section = None
        min_special = float('inf')

        for section in special_counts:
            if any(df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == section)]['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts)):
                continue
            if lively_counts[section] > 0 and limit_one_per_class:
                continue
            same_gender_count = len(df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == section) & (df['ΦΥΛΟ'] == gender)])
            if same_gender_count > 0:
                continue
            if special_counts[section] < min_special:
                min_special = special_counts[section]
                best_section = section

        if best_section:
            df.at[idx, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = best_section
            special_counts[best_section] += 1

    return df


