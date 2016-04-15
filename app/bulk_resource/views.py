import csv
from datetime import datetime

from flask import redirect, render_template, url_for
from flask.ext.login import current_user, login_required

from . import bulk_resource
from .. import db
from ..models import (
    CsvBodyCell,
    CsvBodyRow,
    CsvContainer,
    CsvHeaderCell,
    CsvHeaderRow,
)
from forms import (
    DetermineDescriptorTypesForm,
    DetermineOptionsForm,
    UploadForm
)


@bulk_resource.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new resources in bulk with CSV file."""
    form = UploadForm()
    if form.validate_on_submit():
        csv_data = form.csv.data
        with csv_data.stream as csv_file:
            # Create new CSV container object to hold contents of CSV file.
            csv_container = CsvContainer(
                date_uploaded=datetime.now(),
                file_name=csv_data.filename,
                user=current_user
            )
            csv_reader = csv.reader(csv_file)

            # The first row of the CSV file contains the names of the columns.
            header_row = csv_reader.next()
            csv_header_row = CsvHeaderRow(
                csv_header_row_container=csv_container
            )
            for column_name in header_row:
                csv_cell = CsvHeaderCell(data=column_name,
                                         csv_header_row=csv_header_row)
                db.session.add(csv_cell)
            db.session.add(csv_header_row)

            # Iterate through the CSV file row-by-row and then cell-by-cell.
            # Each cell contains one comma-separated string in a row of a CSV
            # file.
            for row in csv_reader:
                csv_body_row = CsvBodyRow(csv_container=csv_container)
                for cell_data in row:
                    csv_cell = CsvBodyCell(data=cell_data,
                                           csv_body_row=csv_body_row)
                    db.session.add(csv_cell)
                db.session.add(csv_body_row)
            db.session.add(csv_container)
            db.session.commit()

            # TODO: Error catching if CSV is malformed.
            # TODO: Check that CSV file has "Name", "Address", "Description"
            # TODO: headings

        return redirect(url_for('bulk_resource.review1'))
    return render_template('bulk_resource/upload.html', form=form)


@bulk_resource.route('/review1', methods=['GET', 'POST'])
@login_required
def review1():
    csv_container = CsvContainer.query.filter_by(user=current_user).first()
    # TODO: Redirect to 404 if no current CSV is being uploaded.
    form = DetermineDescriptorTypesForm()
    if form.validate_on_submit():
        if form.navigation.data['submit_next']:
            for i, descriptor_type in enumerate(form.descriptor_types.data):
                if descriptor_type == 'text':
                    csv_container.header_row.descriptor_type = descriptor_type
                elif descriptor_type == 'option':
                    csv_container.header_row.descriptor_type = descriptor_type
            return redirect(url_for('bulk_resource.review2'))
        elif form.navigation.data['submit_back']:
            # TODO: Delete all associated CSV objects.
            return redirect(url_for('bulk_resource.upload'))
        elif form.navigation.data['submit_cancel']:
            # TODO: Delete all associated CSV objects.
            return redirect(url_for('bulk_resource.upload'))

    # Add one text/option toggle for each CSV header.
    for i, csv_cell in enumerate(csv_container.csv_header_row.csv_cells):
        form.descriptor_types.append_entry()
        form.descriptor_types[i].label = csv_cell.data
        # for i, header_cell in enumerate(csv_container.csv_header_row.
        # csv_cells):
        #
        #     form.descriptor_types.data

    return render_template('bulk_resource/review1.html',
                           csv_container=csv_container,
                           form=form)


@bulk_resource.route('/review2', methods=['GET', 'POST'])
@login_required
def review2():
    csv_container = CsvContainer.query.filter_by(user=current_user).first()
    # TODO: Redirect to 404 if no current CSV is being uploaded.
    form = DetermineOptionsForm()
    if form.validate_on_submit():
        if form.navigation.data['submit_next']:
            return redirect(url_for('bulk_resource.review2'))
        elif form.navigation.data['submit_back']:
            # TODO: Delete all associated CSV objects.
            return redirect(url_for('bulk_resource.review1'))
        elif form.navigation.data['submit_cancel']:
            # TODO: Delete all associated CSV objects.
            return redirect(url_for('bulk_resource.upload'))

    # Add one text/option toggle for each CSV header.
    for i, csv_cell in enumerate(csv_container.csv_header_row.csv_cells):
        form.options.append_entry()
        form.options[i].label = csv_cell.data

    return render_template('bulk_resource/review2.html',
                           csv_container=csv_container,
                           form=form)
