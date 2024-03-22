from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from database import db

domains_bp = Blueprint('domains', __name__)

table_name = 'domain_table'

class Domains(db.Model):
    __tablename__ = "domain_table"
 
    domain_id = db.Column(db.Integer, primary_key=True, unique=True)
    domain = db.Column(db.String(500), nullable=False)
    subdomain = db.Column(db.String(500), nullable=True)
    subdomain_2 = db.Column(db.String(500), nullable=True)


@domains_bp.route("/domains", methods=['GET', 'POST'])
def home(message=None):
    details = Domains.query.all()
    return render_template("domains/home.html", details=details, message=message)
 
@domains_bp.route("/domains/add", methods=['GET', 'POST'])
def add_domains(message=None):
    if request.method == 'POST':
        domain = request.form['domain']
        subdomain = request.form['subdomain']
        subdomain_2 = request.form['subdomain_2']
        try:
            db.session.execute(text(f"INSERT INTO {table_name} (domain, subdomain, subdomain_2) VALUES ('{domain}', '{subdomain}', '{subdomain_2}')"))
            db.session.commit()
            db.session.close()
            message = "Domain added successfully"
            return render_template("domains/domains.html", message=message)
        except Exception as e:
            db.session.rollback()
            print(e)
            message = "An error occurred while adding the Domain. Please check your inputs."
            return render_template("domains/domains.html", message=message)
 
    return render_template("domains/domains.html", message=message)

@domains_bp.route("/domains/update/<int:domain_id>", methods=['GET', 'POST'])
def update_domain(domain_id, message=None):
    domain = Domains.query.get_or_404(domain_id)
    if request.method == 'POST':
        domain = request.form['domain']
        subdomain = request.form['subdomain']
        subdomain_2 = request.form['subdomain_2']
        try:
            db.session.execute(text(f"UPDATE {table_name} SET domain = '{domain}', subdomain = '{subdomain}', subdomain_2 = '{subdomain_2}' WHERE domain_id = {domain_id}"))
            db.session.commit()
            db.session.close()
            message = "Domain updated successfully"
            domain = Domains.query.get_or_404(domain_id)
            return render_template("domains/update_domain.html", domain=domain, message=message)
        except Exception as e:
            db.session.rollback() 
            print(e)
            message = "An error occurred while updating the domain. Please check your input."
            return render_template("domains/update_domain.html", domain=domain, message=message)
    
    return render_template("domains/update_domain.html", domain=domain, message=message)

@domains_bp.route("/domains/delete/<int:domain_id>", methods=['POST'])
def delete_domain(domain_id):
    if request.method == 'POST':
        try:
            db.session.execute(text(f"DELETE FROM {table_name} WHERE domain_id = {domain_id}"))
            db.session.commit()
            db.session.close()
            message = "domain deleted successfully"
            return render_template("domains/home.html", details=Domains.query.all(), message=message)
        except Exception as e:
            db.session.rollback()  
            print(e)
            message = "An error occurred while deleting the entry. Please check if reference to this entry exists in other tables."
            return render_template("domains/home.html", details=Domains.query.all(), message=message)
        
