import csv
import mysql.connector

# --- UPDATE YOUR DATABASE CREDENTIALS HERE ---
db_config = {
    'user': 'root',
    'password': 'Dragon@123', # <--- PUT YOUR MYSQL PASSWORD HERE
    'host': '127.0.0.1',
    'database': 'educational_platform_db'
}

CSV_FILE_NAME = 'Untitled spreadsheet - Mapped Math Syllabus.csv'

def seed_data():
    """
    Reads the curriculum CSV, cleans the data, and populates the database tables.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("Successfully connected to the database for seeding.")

        # Cache to avoid re-inserting the same items
        grades_map, subjects_map, units_map = {}, {}, {}
        
        print("Starting to process CSV file...")
        with open(CSV_FILE_NAME, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None) # Skip header row

            for i, row in enumerate(reader):
                # Ensure the row has enough columns before processing
                if len(row) < 4:
                    print(f"Skipping short row {i+1}: {row}")
                    continue

                # Clean and extract data
                unit_name = row[0].strip().replace('"', '')
                topic_name = row[1].strip().replace('"', '')
                grade_name_raw = row[2].strip().replace('"', '')
                curriculum_type = row[3].strip().replace('"', '')

                # --- DATA VALIDATION ---
                # If any of the essential fields are empty, skip the row.
                if not all([unit_name, topic_name, grade_name_raw, curriculum_type]):
                    print(f"Skipping row {i+1} due to missing data.")
                    continue

                # If the 'grade' field doesn't seem like a grade, skip it.
                # This prevents topics like "Absolute Value" from becoming grades.
                if 'grade' not in grade_name_raw.lower() and 'algebra' not in grade_name_raw.lower() and 'geometry' not in grade_name_raw.lower() and 'amc' not in grade_name_raw.lower() and 'ib' not in grade_name_raw.lower():
                    print(f"Skipping row {i+1} with unlikely grade: '{grade_name_raw}'")
                    continue
                
                # --- DATA STANDARDIZATION ---
                # Standardize the grade name to prevent duplicates like "9th Grade" and "9th grade"
                grade_name = grade_name_raw.replace('grade', 'Grade').replace('Grade',' Grade').strip()
                grade_name = ' '.join(grade_name.split()) # Remove extra spaces


                # 1. Get or Create Grade ID
                if grade_name not in grades_map:
                    cursor.execute("INSERT INTO tbl_Grade (GradeName, CreatedBy) VALUES (%s, %s)", (grade_name, 'SEEDER'))
                    grades_map[grade_name] = cursor.lastrowid
                grade_id = grades_map[grade_name]

                # 2. Get or Create Subject (Curriculum) ID
                if curriculum_type not in subjects_map:
                    cursor.execute("INSERT INTO tbl_Subject (SubjectName, SubjectType, CreatedBy) VALUES (%s, %s, %s)", (curriculum_type, 'Curriculum', 'SEEDER'))
                    subjects_map[curriculum_type] = cursor.lastrowid
                subject_id = subjects_map[curriculum_type]

                # 3. Get or Create Unit (as a Parent Topic) ID
                unit_key = f"{unit_name}_{subject_id}"
                if unit_key not in units_map:
                    cursor.execute("INSERT INTO tbl_Topic (TopicName, SubjectID, ParentTopicID, CreatedBy) VALUES (%s, %s, NULL, %s)", (unit_name, subject_id, 'SEEDER'))
                    units_map[unit_key] = cursor.lastrowid
                unit_topic_id = units_map[unit_key]

                # 4. Create the actual Topic (as a child of the Unit)
                cursor.execute("INSERT INTO tbl_Topic (TopicName, SubjectID, ParentTopicID, CreatedBy) VALUES (%s, %s, %s, %s)", (topic_name, subject_id, unit_topic_id, 'SEEDER'))
                child_topic_id = cursor.lastrowid
                
                # 5. Link the child Topic to the Grade
                cursor.execute("INSERT INTO tbl_TopicGrade (TopicID, GradeID, CreatedBy) VALUES (%s, %s, %s)", (child_topic_id, grade_id, 'SEEDER'))

        conn.commit()
        print(f"\nDatabase seeding completed successfully! Processed {i+1} valid rows.")

    except mysql.connector.Error as err: print(f"Database Error: {err}")
    except FileNotFoundError: print(f"Error: The file '{CSV_FILE_NAME}' was not found.")
    except Exception as e: print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    seed_data()