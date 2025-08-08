import os
import base64
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

class ReportAgent:
    """
    An agent that generates a final, human-readable HTML report from the
    VotingAgent's final report object.
    """

    def __init__(self):
        """Initializes the ReportAgent."""
        self.templates_dir = 'templates'
        self.reports_dir = 'reports'
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        
        # Set up Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        self.template = self.env.get_template('audit_report_template.html')
        print("ReportAgent is ready.")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Reads an image file and encodes it to a base64 string."""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Warning: Image file not found at {image_path}. Plot will be missing from report.")
            return ""

    def generate_report(self, final_report: Dict[str, Any]) -> str:
        """
        Generates a self-contained HTML report.

        Args:
            final_report (Dict[str, Any]): The final report object from the VotingAgent.

        Returns:
            The file path to the generated HTML report.
        """
        print("Generating final HTML report...")
        
        # Get the path to the SHAP plot from the XAI report
        shap_plot_path = final_report.get('xai_report', {}).get('global_explanation', {}).get('summary_plot_path', '')
        
        # Encode the image for embedding in the HTML
        shap_image_base64 = self._encode_image_to_base64(shap_plot_path)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Render the HTML template with all the data
        html_content = self.template.render(
            final_report=final_report,
            shap_image_base64=shap_image_base64,
            timestamp=timestamp
        )
        
        # Save the rendered HTML to a file
        report_filename = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"Successfully generated report: {report_path}")
        return report_path
