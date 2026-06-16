import os
import tempfile
from flask import Blueprint, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.pdf_helper import generate_weekly_report

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/weekly', methods=['GET'])
@jwt_required()
def get_weekly_report():
    user_id = int(get_jwt_identity())
    
    try:
        # Create a temporary file to store the PDF
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"doomscroll_shield_report_{user_id}_{int(tempfile.tempdir is not None)}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        # Generate the report
        generate_weekly_report(user_id, pdf_path)
        
        # Stream the file back
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="Weekly_Wellbeing_Report.pdf"
        )
        
    except Exception as e:
        return jsonify({"message": f"Failed to generate report: {str(e)}"}), 500
