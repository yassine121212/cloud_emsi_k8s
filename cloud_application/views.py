from django.shortcuts import render
from django.http import HttpResponse

from subprocess import run
from django.http import JsonResponse
from django.template import loader
from kubernetes import client, config
import os
from django.shortcuts import redirect
from django.urls import reverse



# Create your views here.
def toindex(request):
    return render(request, 'page.html')


def generate_client_values(request):
    try:
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

        if not os.path.exists(file_path):
            return JsonResponse({"error": "Client values file not found."}, status=404)

        # Run helm install with the dynamically generated client-values.yaml
        chart_name = '/home/yasseldev/emsi_chart_ubuntu'
        helm_install_command = [
            'helm', 'install', client_username, f'{chart_name}', '--values', file_path
        ]
        run(helm_install_command, check=True)

        # Load Kubernetes configuration from the default kubeconfig file
        config.load_kube_config()

        # Create an instance of the Kubernetes API client
        api_instance = client.CoreV1Api()

        # Specify the label selector to filter pods by app=client_username
        label_selector = 'app=ubuntu_app'
        print("aaaaaaaa")
        print(label_selector)
        # Retrieve the list of pods
        pods_list = api_instance.list_pod_for_all_namespaces(label_selector=label_selector)

        print(pods_list)
        # Extract pod names from the list
        pod_names = [pod.metadata.name for pod in pods_list.items]
        print(pod_names)
        print("xxxxxx")
        # Select one pod name (you can customize this logic)
        selected_pod_name = None

        # Iterate through pod_names to find the first pod that begins with "emsi"
        for pod_name in pod_names:
            if pod_name.startswith(client_username):
                selected_pod_name = pod_name
                break  # Stop the loop once a matching pod is found
        print(selected_pod_name)
        print("bbbbbbbbbbb")
        success_message = f"Helm chart installed for client: {client_username}, Pod Name: {selected_pod_name}"
        return redirect(
            reverse('ubuntu_instance') + f'?success_message={success_message}')
    except Exception as e:
        # Handle other exceptions
        error_message = f"An unexpected error occurred: {str(e)}"
        return JsonResponse({"error": error_message}, status=500)


def ubuntu_instance(request):
    success_message = request.GET.get('success_message', None)
    context = {'success_message': success_message}
    return render(request, 'Services/ubuntu_instance.html', context)


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
