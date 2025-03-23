import functions_framework
import google.auth
from googleapiclient.discovery import build

@functions_framework.http
def scale_up(request):
    """Cloud Function to scale up the instance group."""
    credentials, project = google.auth.default()
    service = build('compute', 'v1', credentials=credentials)

    request_json = request.get_json()
    instance_group = request_json.get('instance_group')
    zone = request_json.get('zone')

    if not instance_group or not zone:
        return "Missing instance_group or zone in request", 400

    try:
        request = service.instanceGroupManagers().resize(
            project=project,
            zone=zone,
            instanceGroupManager=instance_group,
            size=2  # Increase instances
        )
        request.execute()
        return "Scaling request sent.", 200
    except Exception as e:
        return f"Error: {str(e)}", 500
