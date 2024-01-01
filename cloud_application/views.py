from django.shortcuts import render
import os
from subprocess import run, PIPE
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import reverse
# Create your views here.
def toindex(request):
    return render(request, 'page.html')
def generate_client_values(request):
    # Get client-specific input (username, password) from the form
    client_username = request.POST.get('client_username')
    client_password = request.POST.get('client_password')

    # Load a template for client-values.yaml
    template = loader.get_template('client_values_template.yaml')

    # Render the template with client-specific values
    client_values_content = template.render({
        'client_username': client_username,
        'client_password': client_password,
    })
    filename = f'client-{client_username}-values.yaml'

    # Save the generated content to a file in /home/yasseldev/Downloads
    file_path = os.path.join('/home/yasseldev/Downloads', filename)
    with open(file_path, 'w') as file:
        file.write(client_values_content)
        
    file_path = f'/home/yasseldev/Downloads/client-{client_username}-values.yaml'
    if not os.path.exists(file_path):
        return HttpResponse("Client values file not found.", status=404)

    # Run helm install with the dynamically generated client-values.yaml
    chart_name = '/home/yasseldev/emsi_chart_ubuntu'
    helm_install_command = [
        'helm', 'install', client_username, f'{chart_name}', '--values', file_path
    ]

    run(helm_install_command, check=True)

    return HttpResponse(f"Helm chart installed for client: {client_username}")
def package_and_push_chart(request, client_username):
    # Get the username from the URL parameter or request data
    client_username = request.GET.get('client_username')  # Adjust if needed

    # Check if the generated client-values.yaml file exists
    file_path = f'/home/yasseldev/Downloads/client-{client_username}-values.yaml'
    if not os.path.exists(file_path):
        return HttpResponse("Client values file not found.", status=404)

    # Run helm install with the dynamically generated client-values.yaml
    chart_name = '/home/yasseldev/emsi_chart_ubuntu'
    helm_install_command = [
        'helm', 'install', client_username, f'{chart_name}', '--values', file_path
    ]

    run(helm_install_command, check=True)

    return HttpResponse(f"Helm chart installed for client: {client_username}")
