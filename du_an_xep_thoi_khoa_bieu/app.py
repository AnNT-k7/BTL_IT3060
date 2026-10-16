import hashlib
from pathlib import Path

import streamlit as st

from timetable_ai.core import InputError, Slot, explain_slot, export_csv, improve_schedule, load_directory, load_text, score, solve, validate_schedule

st.set_page_config(page_title='Xếp thời khóa biểu AI', layout='wide')
st.title('Xếp thời khóa biểu học phần')
st.caption('Dữ liệu demo là dữ liệu mô phỏng; lịch lặp lại theo tuần.')

default_path = Path(__file__).parent / 'data' / 'demo'
st.header('1. Dữ liệu')
uploads = st.file_uploader('Tải CSV/JSON (hoặc để trống dùng bộ demo)', type=('csv', 'json'), accept_multiple_files=True)
try:
    if uploads:
        if len({item.name for item in uploads}) != len(uploads):
            raise InputError('Có tệp tải lên trùng tên')
        files = {item.name: item.getvalue().decode('utf-8-sig') for item in uploads}
        signature = hashlib.sha256(repr(sorted(files.items())).encode('utf-8')).hexdigest()
        problem = load_text(files)
    else:
        signature = 'demo'
        problem = load_directory(default_path)
    if st.session_state.get('source_signature') != signature:
        st.session_state['source_signature'] = signature
        st.session_state['availability_overrides'] = {}
        st.session_state.pop('result', None)
        st.session_state.pop('previous_assignment', None)
    for key, available in st.session_state['availability_overrides'].items():
        problem.availability[key] = available
    st.success(f'{len(problem.sessions)} buổi, {len(problem.rooms)} phòng')
except (InputError, UnicodeError) as exc:
    st.error(str(exc))
    st.stop()

with st.expander('Thử thay đổi giờ rảnh của giảng viên'):
    teacher = st.selectbox('Giảng viên', sorted({s.teacher_id for s in problem.sessions}))
    day = st.selectbox('Ngày', problem.days)
    period = st.selectbox('Tiết', list(range(1, problem.periods_per_day + 1)))
    availability_key = (teacher, day, period)
    available = st.checkbox('Có thể dạy', value=problem.availability.get(availability_key, False),
                            key=f'availability_{signature}_{teacher}_{day}_{period}')
    if available != problem.availability.get(availability_key, False):
        st.session_state['availability_overrides'][availability_key] = available
        problem.availability[availability_key] = available
        if st.session_state.get('result', {}).get('assignment'):
            st.session_state['previous_assignment'] = dict(st.session_state['result']['assignment'])
        st.session_state.pop('result', None)
    if st.session_state['availability_overrides']:
        st.caption(f"Đã thay đổi {len(st.session_state['availability_overrides'])} ô giờ rảnh. Bấm 'Xếp lịch' để áp dụng.")

st.header('2. Chạy thuật toán')
solver = st.selectbox('Bộ giải', ('enhanced', 'baseline'))
limit = st.number_input('Giới hạn tìm lịch (giây)', min_value=0.0, value=float(problem.time_limit_seconds))
for key, label in (('late_periods', 'Tiết muộn'), ('student_gaps', 'Tiết trống nhóm'), ('preference_penalty', 'Giờ không ưa thích')):
    problem.weights[key] = st.number_input(f'Trọng số: {label}', min_value=0.0, value=float(problem.weights[key]))
optimize = st.checkbox('Cải thiện điểm phạt sau khi tìm lịch', value=True)
optimization_limit = st.number_input('Giới hạn tối ưu cục bộ (giây, cộng thêm)',
                                     min_value=0.0, value=2.0, disabled=not optimize)
settings = (solver, limit, tuple(sorted(problem.weights.items())), optimize,
            optimization_limit, tuple(sorted(st.session_state['availability_overrides'].items())))
if 'result' in st.session_state and settings != st.session_state.get('last_settings'):
    if st.session_state['result'].get('assignment'):
        st.session_state['previous_assignment'] = dict(st.session_state['result']['assignment'])
    st.session_state.pop('result', None)
if st.button('Xếp lịch', type='primary'):
    if st.session_state.get('result', {}).get('assignment'):
        st.session_state['previous_assignment'] = dict(st.session_state['result']['assignment'])
    st.session_state['result'] = solve(problem, solver, limit)
    st.session_state['problem'] = problem
    st.session_state['last_settings'] = settings
    st.session_state['optimization'] = None
    if optimize and st.session_state['result']['assignment']:
        improved = improve_schedule(problem, st.session_state['result']['assignment'], time_limit=optimization_limit)
        st.session_state['result']['assignment'] = improved['assignment']
        st.session_state['optimization'] = improved

if 'result' in st.session_state:
    result = st.session_state['result']
    problem = st.session_state['problem']
    st.header('3. Kết quả')
    labels = {'FEASIBLE': 'Có lịch hợp lệ', 'UNSAT': 'Đã chứng minh vô nghiệm', 'TIMEOUT': 'Không tìm thấy lịch trong thời hạn'}
    st.write(labels[result['status']])
    st.json({key: result[key] for key in ('status', 'elapsed_seconds', 'nodes', 'backtracks', 'pruned')})
    with st.expander('Dấu vết MRV / forward checking'):
        st.write('\n'.join(result['trace']))
    if result['assignment']:
        errors = validate_schedule(problem, result['assignment'])
        if errors:
            st.error(errors)
            st.stop()
        st.json(score(problem, result['assignment']))
        if st.session_state.get('optimization'):
            improvement = st.session_state['optimization']
            st.write(f"Tối ưu cục bộ: {improvement['moves']} lần thay đổi; điểm phạt {improvement['before']['total']} → {improvement['after']['total']}")
        previous = st.session_state.get('previous_assignment')
        if previous and set(previous) == set(result['assignment']):
            changed = sum(previous[sid] != slot for sid, slot in result['assignment'].items())
            st.info(f'So với lịch ở lần chạy trước: {changed}/{len(previous)} buổi đổi vị trí.')
        with st.expander('Kiểm tra một khung giờ đề xuất'):
            proposed_session = st.selectbox('Buổi cần chuyển', [s.session_id for s in problem.sessions])
            proposed_day = st.selectbox('Ngày đề xuất', problem.days)
            proposed_period = st.selectbox('Tiết bắt đầu đề xuất', list(range(1, problem.periods_per_day + 1)))
            proposed_room = st.selectbox('Phòng đề xuất', [r.room_id for r in problem.rooms])
            reasons = explain_slot(problem, result['assignment'], proposed_session,
                                   Slot(proposed_day, proposed_period, proposed_room))
            if reasons:
                for reason in reasons:
                    st.warning(reason)
            else:
                st.success('Khung giờ này không vi phạm ràng buộc cứng khi chuyển buổi đã chọn.')
        rows = []
        for session in problem.sessions:
            slot = result['assignment'][session.session_id]
            rows.append({'Buổi': session.session_id, 'Môn': session.course_id, 'Ngày': slot.day,
                         'Tiết bắt đầu': slot.period, 'Số tiết': session.duration, 'Phòng': slot.room_id,
                         'Giảng viên': session.teacher_id, 'Nhóm': session.group_id})
        view = st.selectbox('Xem theo', ('Nhóm', 'Giảng viên', 'Phòng'))
        field = {'Nhóm': 'Nhóm', 'Giảng viên': 'Giảng viên', 'Phòng': 'Phòng'}[view]
        choice = st.selectbox('Chọn', sorted({row[field] for row in rows}))
        selected = [row for row in rows if row[field] == choice]
        grid = []
        for period in range(1, problem.periods_per_day + 1):
            cells = {'Tiết': period}
            for day in problem.days:
                occupied = [r for r in selected if r['Ngày'] == day and r['Tiết bắt đầu'] <= period < r['Tiết bắt đầu'] + r['Số tiết']]
                cells[day] = ', '.join(f"{r['Môn']} / {r['Phòng']} / {r['Giảng viên']}" for r in occupied)
            grid.append(cells)
        st.subheader('Lưới thời khóa biểu')
        st.dataframe(grid, hide_index=True, width='stretch')
        st.dataframe(selected, hide_index=True)
        st.dataframe(rows, hide_index=True)
        st.download_button('Tải lịch CSV', export_csv(problem, result['assignment']), 'schedule.csv', 'text/csv')
