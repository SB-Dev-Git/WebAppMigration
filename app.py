from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import sqlite3
import csv
import os
from datetime import datetime, date
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def init_db():
    conn = sqlite3.connect('kintai.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            day_of_week TEXT NOT NULL,
            type TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            break_time INTEGER DEFAULT 0,
            work_hours REAL DEFAULT 0,
            comment TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_day_of_week(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    days = ['月', '火', '水', '木', '金', '土', '日']
    return days[date_obj.weekday()]

def calculate_work_hours(start_time, end_time, break_time):
    if not start_time or not end_time:
        return 0
    
    try:
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        
        diff_minutes = (end - start).total_seconds() / 60
        
        work_minutes = diff_minutes - break_time
        
        return round(work_minutes / 60, 2) if work_minutes > 0 else 0
    except:
        return 0

def validate_time_input(start_time, end_time, break_time):
    errors = []
    
    if start_time and end_time:
        try:
            start = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
            
            if end <= start:
                errors.append('退勤時間は出勤時間より後である必要があります')
                
            total_minutes = (end - start).total_seconds() / 60
            if break_time >= total_minutes:
                errors.append('休憩時間は勤務時間より短い必要があります')
                
        except ValueError:
            errors.append('時間の形式が正しくありません（HH:MM形式で入力してください）')
    
    if break_time < 0:
        errors.append('休憩時間は0以上である必要があります')
    
    return errors

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=['GET', 'POST'])
def input_attendance():
    if request.method == 'POST':
        date_str = request.form['date']
        attendance_type = request.form['type']
        start_time = request.form.get('start_time', '')
        end_time = request.form.get('end_time', '')
        break_time = int(request.form.get('break_time', 0))
        comment = request.form.get('comment', '')
        
        errors = validate_time_input(start_time, end_time, break_time)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('input.html', 
                                 date=date_str, 
                                 type=attendance_type,
                                 start_time=start_time,
                                 end_time=end_time,
                                 break_time=break_time,
                                 comment=comment)
        
        day_of_week = get_day_of_week(date_str)
        work_hours = calculate_work_hours(start_time, end_time, break_time)
        
        conn = sqlite3.connect('kintai.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO attendance 
                (date, day_of_week, type, start_time, end_time, break_time, work_hours, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date_str, day_of_week, attendance_type, start_time, end_time, break_time, work_hours, comment))
            
            conn.commit()
            flash('勤怠データを保存しました', 'success')
            
        except sqlite3.Error as e:
            flash(f'データベースエラー: {e}', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('input_attendance'))
    
    today = date.today().strftime('%Y-%m-%d')
    return render_template('input.html', date=today)

@app.route('/display')
def display_attendance():
    conn = sqlite3.connect('kintai.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, day_of_week, type, start_time, end_time, break_time, work_hours, comment
        FROM attendance
        ORDER BY date DESC
    ''')
    
    records = cursor.fetchall()
    conn.close()
    
    return render_template('display.html', records=records)

@app.route('/export_csv')
def export_csv():
    conn = sqlite3.connect('kintai.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, day_of_week, type, start_time, end_time, break_time, work_hours, comment
        FROM attendance
        ORDER BY date
    ''')
    
    records = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['日付', '曜日', '種別', '出勤時間', '退勤時間', '休憩時間', '実働時間', 'コメント'])
    
    for record in records:
        writer.writerow(record)
    
    today = datetime.now().strftime('%Y%m%d')
    filename = f'kintai_{today}.csv'
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename=filename
    )

@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルが選択されていません', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('ファイルが選択されていません', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            try:
                stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
                csv_reader = csv.reader(stream)
                
                next(csv_reader)
                
                conn = sqlite3.connect('kintai.db')
                cursor = conn.cursor()
                
                imported_count = 0
                for row in csv_reader:
                    if len(row) >= 8:
                        date_str, day_of_week, attendance_type, start_time, end_time, break_time_str, work_hours_str, comment = row[:8]
                        
                        break_time = int(break_time_str) if break_time_str else 0
                        work_hours = float(work_hours_str) if work_hours_str else 0
                        
                        errors = validate_time_input(start_time, end_time, break_time)
                        if not errors:
                            cursor.execute('''
                                INSERT OR REPLACE INTO attendance 
                                (date, day_of_week, type, start_time, end_time, break_time, work_hours, comment)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (date_str, day_of_week, attendance_type, start_time, end_time, break_time, work_hours, comment))
                            imported_count += 1
                
                conn.commit()
                conn.close()
                
                flash(f'{imported_count}件のデータをインポートしました', 'success')
                
            except Exception as e:
                flash(f'CSVファイルの処理中にエラーが発生しました: {e}', 'error')
        else:
            flash('CSVファイルを選択してください', 'error')
        
        return redirect(url_for('import_csv'))
    
    return render_template('import.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
