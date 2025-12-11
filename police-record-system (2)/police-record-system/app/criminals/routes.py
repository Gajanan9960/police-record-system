from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.criminals import criminals
from app.forms import CriminalForm
from app.models import Criminal

@criminals.route('/criminals')
@login_required
def list_criminals():
    criminals_list = Criminal.query.all()
    return render_template('criminals.html', criminals=criminals_list)

@criminals.route('/criminals/add', methods=['GET', 'POST'])
@login_required
def add_criminal():
    form = CriminalForm()
    if form.validate_on_submit():
        criminal = Criminal(name=form.name.data, aliases=form.aliases.data,
                            dob=form.dob.data, gender=form.gender.data,
                            address=form.address.data, status=form.status.data)
        db.session.add(criminal)
        db.session.commit()
        flash('Criminal record added!', 'success')
        return redirect(url_for('criminals.list_criminals'))
    return render_template('add_criminal.html', title='Add Criminal', form=form)
