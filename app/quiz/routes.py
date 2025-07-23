from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from ..models import Quiz, Question, Answer, User, GameSesh, Player
from ..extensions import db,sockatia
from .forms import Quiz_form, Question_form, Join_game_form
from flask_socketio import join_room,leave_room,emit
import random
import string


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

    code = ''.join(random.choices(string.digits, k=6))

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
        Game_sesh = GameSesh.query.filter_by(code=form.code.data, is_active=True).first()
        if Game_sesh:
            return redirect(url_for('quiz.Play_sesh', code=form.code.data, username=form.username.data))
        else:
            flash('U dumb, try a different code lol','danger')
    return render_template('quiz/join.html', form=form)

@quiz_bp.route('/play/<code>/<username>')
def Play_sesh(code,username):
    Game_sesh = GameSesh.query.filter_by(code=code,is_active=True).first_or_404()
    return render_template('quiz/PlaySesh.html',code=code,username=username)

@sockatia.on('connect')
def Handle_connact():
    print('player sonnested')
@sockatia.on('disconnected')
def Handle_disconnact():
    print('player discsonnested')

@sockatia.on('join')
def Handle_Join(data):
    code = data['code']
    username = data['username']
    sesh_id = request.sid
    Game_sesh = GameSesh.query.filter_by(code=code,is_active=True).first()
    if not Game_sesh:
        emit('error',{'message': "stoobid game code"})
        return
    player = Player.query.filter_by(game_sesh_id=Game_sesh.id,username=username).first()
    if not player:
        player = Player(
            username=username,
            game_sesh_id=Game_sesh.id,
            sid=sesh_id,
            user_id=current_user.id)
        db.session.add(player)
        db.session.commit()
    else:
        player.sid = sesh_id
        db.session.commit()
        flash('u are dumb','success')
    join_room(code)
    emit('player_joined',{'username':username},room=code)
    if Game_sesh.curr_question > 0:
        question = Game_sesh.quiz.questions[Game_sesh.curr_question - 1]
        emit('question', {
            'text': question.text,
            'answers': [{'id': a.id, 'text': a.text} for a in question.answers],
            'question_number': Game_sesh.curr_question,
            'total_questions': len(Game_sesh.quiz.questions)
        }, room=sesh_id)

@sockatia.on('start_game')
def handle_start_game(data):
    try:
        code = data['code']
        print(f"Received start_game event for code: {code}")  # Debug
        
        game_sesh = GameSesh.query.filter_by(code=code).first()
        if not game_sesh:
            print("Game session not found")  # Debug
            emit('error', {'message': 'Game session not found'})
            return
        
        print(f"Found game session for quiz: {game_sesh.quiz.title}")  # Debug
        
        # Reset game state
        game_sesh.current_question = 1
        game_sesh.is_active = True
        db.session.commit()

        # Get all players in this session
        players = Player.query.filter_by(game_sesh_id=game_sesh.id).all()
        
        # Send game started event to host
        emit('game_started', {
            'status': 'success',
            'message': 'Game started successfully',
            'player_count': len(players)
        }, room=request.sid)
        
        # Send game started event to all players
        emit('game_started', {
            'status': 'success',
            'message': 'Game started!'
        }, room=code)
        
        # Send first question to all
        question = game_sesh.quiz.questions[0]
        emit('question', {
            'text': question.text,
            'answers': [{'id': a.id, 'text': a.text} for a in question.answers],
            'question_number': 1,
            'total_questions': len(game_sesh.quiz.questions)
        }, room=code)

        print("Game started successfully")  # Debug
        
    except Exception as e:
        print(f"Error in start_game: {str(e)}")  # Debug
        emit('error', {'message': str(e)}, room=request.sid)
@sockatia.on('answer')
def handle_answer(data):
    username = data['username']
    code = data['code']
    answer_id = data['answer_id']
    Game_sesh = GameSesh.query.filter_by(code=code).first()
    if not Game_sesh:
        return
    answer = Answer.query.get(answer_id)
    if not answer:
        return
    player = Player.query.filter_by(game_sesh_id=Game_sesh.id,username=username).first()
    if not player:
        return
    if answer.is_right:
        player.score += 100
        db.session.commit()
    emit('answer_received',{'username':username},room=code)

@sockatia.on('next_question')
def handle_next_question(data):
    code = data['code']
    Game_sesh = GameSesh.query.filter_by(code=code).first()
    if not Game_sesh:
        return
    Game_sesh.curr_question += 1
    db.session.commit()
    if Game_sesh.curr_question <= len(Game_sesh.quiz.questions):
        question = Game_sesh.quiz.questions[Game_sesh.curr_question -1]
        emit('question', {
                'text': question.text,
                'answers': [{'id': a.id, 'text': a.text} for a in question.answers],
                'question_number': Game_sesh.curr_question,
                'total_questions': len(Game_sesh.quiz.questions)
            }, room=code)
    else:
        player = Player.query.filter_by(game_sesh_id=Game_sesh.id).order_by(Player.score.desc()).all()
        emit('game_over',{'leaderboard':[{'username':i.username,'score':i.score}for i in player]},room=code)
        Game_sesh.is_active = False
        db.session.commit()


@sockatia.on('host_join')
def handle_host_join(data):
    code = data['code']
    sesh_id = request.sid
    Game_sesh = GameSesh.query.filter_by(code=code, is_active=True).first()
    
    if not Game_sesh:
        emit('error', {'message': "Invalid game code"})
        return
    
    join_room(code)
    print(f'Host joined game with code: {code}')

@quiz_bp.route('/quiz/play/<code>/host')
@login_required
def hosty(code):
    Game_sesh = GameSesh.query.filter_by(code=code).first_or_404()
    return render_template('quiz/host_live.html',code=code)







