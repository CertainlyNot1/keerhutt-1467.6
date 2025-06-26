from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from ..models import Quiz, Question, Answer, User, GameSesh
from ..extensions import db
from .forms import Quiz_form, Question_form, Join_game_form

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz')
@login_required
def quiz_home():
    quizzes = Quiz.query.all()
    return render_template('quiz/home.html', title="Quizzes", quizzes=quizzes)

@quiz_bp.route('/create', methods=['GET','POST'])
@login_required
def create_Qizz():
    form = Quiz_form()
    if form.validate_on_submit():
        quiz = Quiz(title=form.title.data, creator=current_user)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created! Time to add questions!','success')
        return redirect(url_for('quiz.Add_Qistion', quiz_id=quiz.id))
    return render_template('quiz/create_quiz.html', title='Create a quiz!1!!', form=form)

@quiz_bp.route('/quiz/<int:quiz_id>/add_question',methods=['GET','POST'])
@login_required
def Add_Qistion(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = Question_form()
    if form.validate_on_submit():
        question = Question(text=form.text.data,question=quiz)
        db.session.add(question)
        answers = [Answer(text=form.answer1_text.data,is_right=form.Correct_answer.data=='1',question=question),
                   Answer(text=form.answer2_text.data,is_right=form.Correct_answer.data=='2',question=question),
                   Answer(text=form.answer3_text.data,is_right=form.Correct_answer.data=='3',question=question),
                   Answer(text=form.answer4_text.data,is_right=form.Correct_answer.data=='4',question=question)]
        db.session.add_all(answers)
        db.session.commit()
        
        if 'add_more' in request.form:
            flash('Question added! Add more?','success')
            return redirect(url_for('quiz.Add_Qistion',quiz_id=quiz_id))
        else:
            flash('Question added!','success')
            return redirect(url_for('quiz.view_quiz',quiz_id=quiz_id))
    return render_template('quiz/add_question.html',form=form,quiz=quiz,title='Add question!!1!')

@quiz_bp.route('/quiz/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz/view_quiz.html',title=quiz.title, quiz=quiz)

@quiz_bp.route('/quiz/<int:quiz_id>/play', methods=['GET', 'POST'])
@login_required 
def Play_qizz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question_id = request.args.get('question', 1, type=int)
    
    # Get the current question based on the question_id parameter
    current_question = quiz.questions[question_id - 1] if 0 < question_id <= len(quiz.questions) else None
    
    if request.method == 'POST':
        if 'submit_quiz' in request.form:
            # Handle final submission
            score = 0
            total = len(quiz.questions)
            
            # Get all answers from session
            user_answers = session.get(f'quiz_{quiz_id}_answers', {})
            
            for question in quiz.questions:
                answer_id = user_answers.get(str(question.id))
                if answer_id:
                    answer = Answer.query.get(int(answer_id))
                    if answer.is_right:
                        score += 1
            
            # Clear the session data
            session.pop(f'quiz_{quiz_id}_answers', None)
            
            flash(f'You scored {score}/{total}', 'info')
            return redirect(url_for('quiz.quiz_home'))
        else:
            # Store the answer in session
            if current_question:
                selected_answer = request.form.get(f'question_{current_question.id}')
                if selected_answer:
                    if f'quiz_{quiz_id}_answers' not in session:
                        session[f'quiz_{quiz_id}_answers'] = {}
                    session[f'quiz_{quiz_id}_answers'][str(current_question.id)] = selected_answer
                    session.modified = True
            
            # Move to next question or finish
            next_question = question_id + 1
            if next_question <= len(quiz.questions):
                return redirect(url_for('quiz.Play_qizz', quiz_id=quiz_id, question=next_question))
            else:
                return redirect(url_for('quiz.Play_qizz', quiz_id=quiz_id, question=question_id))
    
    return render_template('quiz/play_quiz.html', 
                         title=f'Play {quiz.title}', 
                         quiz=quiz,
                         current_question=current_question,
                         current_question_number=question_id,
                         total_questions=len(quiz.questions))

@quiz_bp.route('/quiz/<int:quiz_id>/delete', methods = ['POST']) 
@login_required 
def delete_qizz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.creator != current_user:
        flash("You Can't delete other's quizzes!",'danger')
        return redirect(url_for('quiz.quiz_home'))
    
    db.session.delete(quiz)
    db.session.commit()
    flash('Deleted system32 successfully!)', 'success')
    return redirect(url_for('quiz.quiz_home'))

@quiz_bp.route('/quiz/<int:quiz_id>/host', methods=['GET'])
@login_required
def host_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    Game_sesh = GameSesh(
        quiz_id=quiz.id,
        code=code,
        is_active = True
    )
    db.session.add(Game_sesh)
    db.session.commit()

    return render_template('quiz/host.html', quiz=quiz, code=code)
@quiz_bp.route('/join', methods=['GET','POST'])
def join_sesh():
    form = Join_game_form()
    if form.validate_on_submit():
        Game_sesh = GameSesh.query._filter_by(code=form.code.data, is_active=True).first()
        if Game_sesh:
            return redirect(url_for('quiz.play_live', code=form.code.data, username=form.username.data))
        else:
            flash('U dumb, try a different code lol','danger')
    return render_template('quiz/join.html', form=form)