from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from database import SessionLocal, engine
from models import Base, Feedback
from datetime import date
from sqlalchemy import func
import math
import json
import os
import uuid

app = Flask(__name__)

# Créer les tables
Base.metadata.create_all(bind=engine)

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configuration des uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Vérifier si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Générer un nom de fichier unique"""
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    return unique_filename


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    db = SessionLocal()
    try:
        # # Récupérer les données du formulaire
        # data = request.form
        # file = request.files.get('attachedfiles')
        
        # Vérification de la taille du fichier
        if request.content_length > MAX_CONTENT_LENGTH:
            return jsonify({"status": "error", "message": "Fichier trop volumineux"}), 413
        
        # Récupérer les données du formulaire
        data = request.form
        file = request.files.get('attachedfiles')

        # Gestion du fichier joint
        filepath = None
        if file and allowed_file(file.filename):
            # Générer un nom de fichier unique et sécurisé
            filename = generate_unique_filename(secure_filename(file.filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Créer le dossier uploads s'il n'existe pas
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Sauvegarder le fichier
            file.save(filepath)
        elif file:
            return jsonify({"status": "error", "message": "Type de fichier non autorisé"}), 400

        # # Gestion du fichier joint
        # filename = None
        # if file:
        #     filename = file.filename
        #     file.save(os.path.join('uploads', filename))

        # Création du feedback avec données JSON
        feedback = Feedback(
            formation=data.get('formation'),
            priorite_retour=data.get('prioriteRetour'),
            type_retour=data.get('typeRetour'),
            date=date.today(),
            rating=int(data.get('rating')),
            comments=data.get('comments'),
            fichier_joint=filename,
            consentement=data.get('consentement') == 'on',
            data_json=json.dumps(dict(data))
        )

        db.add(feedback)
        db.commit()

        return jsonify({"status": "success", "message": "Retour enregistré"})
    
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)})
    
    finally:
        db.close()

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/get_feedbacks')
def get_feedbacks():
    db = SessionLocal()
    
    # Paramètres de pagination et recherche
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_term = request.args.get('search', '').strip()
    
    # Requête de base
    query = db.query(Feedback)
    
    # Recherche
    if search_term:
        search_filter = f"%{search_term}%"
        query = query.filter(
            (Feedback.formation.like(search_filter)) |
            (Feedback.type_retour.like(search_filter)) |
            (Feedback.comments.like(search_filter))
        )
    
    # Comptage total
    total_count = query.count()
    
    # Pagination
    offset = (page - 1) * per_page
    feedbacks = query.order_by(Feedback.id.desc()).offset(offset).limit(per_page).all()
    
    # Calcul du nombre total de pages
    total_pages = math.ceil(total_count / per_page)
    
    # Transformation des données
    feedback_list = []
    for feedback in feedbacks:
        feedback_dict = {
            'id': feedback.id,
            'formation': feedback.formation,
            'priorite_retour': feedback.priorite_retour,
            'type_retour': feedback.type_retour,
            'date': feedback.date.strftime('%d/%m/%Y'),
            'rating': feedback.rating,
            'comments': feedback.comments,
            'fichier_joint': feedback.fichier_joint
        }
        feedback_list.append(feedback_dict)
    
    db.close()
    
    return jsonify({
        'feedbacks': feedback_list,
        'total_pages': total_pages,
        'current_page': page,
        'total_count': total_count
    })

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)