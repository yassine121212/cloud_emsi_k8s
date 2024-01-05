from django.shortcuts import render
from django.http import HttpResponse
import subprocess

from subprocess import run
from django.http import JsonResponse
from django.template import loader
from kubernetes import client, config
import os
from django.shortcuts import redirect
from django.urls import reverse
import time


# Create your views here.
def toindex(request):
    return render(request, 'page.html')


def get_service_external_ip(service_name, namespace="default"):
    try:
        # Load Kubernetes configuration from the default kubeconfig file
        config.load_kube_config()

        # Create an instance of the Kubernetes API client
        api_instance = client.CoreV1Api()

        # Retrieve the service information
        service_info = api_instance.read_namespaced_service(name=service_name, namespace=namespace)

        # Extract the external IP address
        external_ip = service_info.status.load_balancer.ingress[0].ip
        return external_ip

    except Exception as e:
        print(f"Error retrieving external IP address: {str(e)}")
        return None


# Usage example

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
        print("zoz : ", filename)

        # Save the generated content to a file in /home/yasseldev/Downloads
        file_path = os.path.join('/home/yasseldev/Downloads', filename)
        try:
            with open(file_path, 'w') as file:
                file.write(client_values_content)
        except Exception as file_error:
            return JsonResponse({"error": f"Error creating file: {str(file_error)}"}, status=500)

        if not os.path.exists(file_path):
            return JsonResponse({"error": "Client values file not found."}, status=404)

        try:
            # Run helm install with the dynamically generated client-values.yaml
            chart_name = '/home/yasseldev/emsi_chart_ubuntu'
            helm_install_command = [
                'helm', 'install', client_username, f'{chart_name}', '--values', file_path
            ]
            subprocess.run(helm_install_command, check=True)
        except Exception as helm_error:
            return JsonResponse({"error": f"Helm installation failed: {str(helm_error)}"}, status=500)

        # Load Kubernetes configuration from the default kubeconfig file
        config.load_kube_config()

        # Create an instance of the Kubernetes API client
        api_instance = client.CoreV1Api()

        # Specify the label selector to filter pods by app=client_username
        label_selector = 'app=ubuntu_app'
        print("Label Selector:", label_selector)

        # Retrieve the list of pods
        pods_list = api_instance.list_pod_for_all_namespaces(label_selector=label_selector)

        print("Pods List:", pods_list)
        with open(file_path, 'r') as file:
            file_content = file.read()
            print(f"Content of {filename}:\n{file_content}")

        # Extract pod names from the list
        pod_names = [pod.metadata.name for pod in pods_list.items]
        print("Pod Names:", pod_names)

        # Select one pod name (you can customize this logic)
        selected_pod_name = next((pod_name for pod_name in pod_names if pod_name.startswith(client_username)), None)

        service_name = selected_pod_name
        time.sleep(4)
        result = service_name.split("-")[0] + "-service"
        print(result)

        install_command = ["kubectl",
                           "get",
                           "svc",
                           result,
                           "-o=jsonpath='{.status.loadBalancer.ingress[0].ip}'"
                           ]

        try:
            result = subprocess.run(install_command, check=True, capture_output=True, text=True)
            output = result.stdout.strip()
            print(f"The IP address is: {output}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing the command: {e}")

        success_message = selected_pod_name
        return redirect(reverse('ubuntu_instance') + f'?success_message={success_message}&ip_address={output}')

    except Exception as e:
        # Handle other exceptions
        error_message = f"An unexpected error occurred: {str(e)}"
        return JsonResponse({"error": error_message}, status=500)


def ubuntu_instance(request):
    success_message = request.GET.get('success_message')
    ip_address = request.GET.get('ip_address').strip("\'")
    print("zeeee")
    print(ip_address)

    context = {
        'success_message': success_message,
        'ip_address': ip_address,
    }

    return render(request, 'Services/ubuntu_instance.html', context)


# def package_and_push_chart(request, client_username):
#     # Get the username from the URL parameter or request data
#     client_username = request.GET.get('client_username')  # Adjust if needed
#
#     # Check if the generated client-values.yaml file exists
#     file_path = f'/home/yasseldev/Downloads/client-{client_username}-values.yaml'
#     if not os.path.exists(file_path):
#         return HttpResponse("Client values file not found.", status=404)
#
#     # Run helm install with the dynamically generated client-values.yaml
#     chart_name = '/home/yasseldev/emsi_chart_ubuntu'
#     helm_install_command = [
#         'helm', 'install', client_username, f'{chart_name}', '--values', file_path
#     ]
#
#     run(helm_install_command, check=True)
#
#     return HttpResponse(f"Helm chart installed for client: {client_username}")


def next_cloud_generate_service_client_values(request):
    try:
        # Get client-specific input (username, password) from the form
        service_client_username = request.POST.get('service_client_username')

        # Load a template for service-client-values.yaml
        template = loader.get_template('service_values_template.yaml')

        # Render the template with service-client-specific values
        service_client_values_content = template.render({
            'client_username': service_client_username,
        })

        filename = f'service-client-{service_client_username}-values.yaml'
        print("zoz : ", filename)

        # Save the generated content to a file in /home/yasseldev/Downloads
        file_path = os.path.join('/home/yasseldev/Downloads', filename)
        try:
            with open(file_path, 'w') as file:
                file.write(service_client_values_content)
        except Exception as file_error:
            return JsonResponse({"error": f"Error creating file: {str(file_error)}"}, status=500)

        if not os.path.exists(file_path):
            return JsonResponse({"error": "service client values file not found."}, status=404)

        try:
            # Run helm install with the dynamically generated service-client-values.yaml
            chart_name = '/home/yasseldev/emsi_chat_nextcloud'
            helm_install_command = [
                'helm', 'install', service_client_username, f'{chart_name}', '--values', file_path
            ]
            subprocess.run(helm_install_command, check=True)
        except Exception as helm_error:
            return JsonResponse({"error": f"Helm installation failed: {str(helm_error)}"}, status=500)

        # Load Kubernetes configuration from the default kubeconfig file
        config.load_kube_config()

        # Create an instance of the Kubernetes API client
        api_instance = client.CoreV1Api()

        # Specify the label selector to filter pods by app=service_client_username
        label_selector = 'app=next_cloud_app'
        print("Label Selector:", label_selector)

        # Retrieve the list of pods
        pods_list = api_instance.list_pod_for_all_namespaces(label_selector=label_selector)

        print("Pods List:", pods_list)
        with open(file_path, 'r') as file:
            file_content = file.read()
            print(f"Content of {filename}:\n{file_content}")

        # Extract pod names from the list
        pod_names = [pod.metadata.name for pod in pods_list.items]
        print("Pod Names:", pod_names)

        # Select one pod name (you can customize this logic)
        selected_pod_name = next((pod_name for pod_name in pod_names if pod_name.startswith(service_client_username)),
                                 None)

        service_name = selected_pod_name
        time.sleep(4)
        result = service_name.split("-")[0] + "-service"
        print(result)

        install_command = ["kubectl",
                           "get",
                           "svc",
                           result,
                           "-o=jsonpath='{.status.loadBalancer.ingress[0].ip}'"
                           ]
        time.sleep(2)

        try:
            result = subprocess.run(install_command, check=True, capture_output=True, text=True)
            output = result.stdout.strip()
            print(f"The IP address is: {output}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing the command: {e}")

        success_message = selected_pod_name
        return redirect(reverse('next_cloud') + f'?success_message={success_message}&ip_address={output}')

    except Exception as e:
        # Handle other exceptions
        error_message = f"An unexpected error occurred: {str(e)}"
        return JsonResponse({"error": error_message}, status=500)


def next_cloud(request):
    success_message = request.GET.get('success_message')
    ip_address = request.GET.get('ip_address').strip("\'")
    print("zeeee")
    print(ip_address)

    context = {
        'success_message': success_message,
        'ip_address': ip_address,
    }

    return render(request, 'Services/next_cloud.html', context)
