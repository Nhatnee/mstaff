from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Contract
from user.models import Employee
from user.models import UserContract  # Import UserContract from user app
from .forms import ContractForm
import logging

logger = logging.getLogger(__name__)

def contract_list(request):
    contracts = Contract.objects.all()
    return render(request, 'contract/contract_list.html', {'contracts': contracts})

def contract_add(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contract added successfully!')
            return redirect('contract_list')
    else:
        form = ContractForm()
    return render(request, 'contract/contract_form.html', {'form': form, 'action': 'Add'})

def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contract updated successfully!')
            return redirect('contract_list')
    else:
        form = ContractForm(instance=contract)
    return render(request, 'contract/contract_form.html', {'form': form, 'action': 'Edit'})

def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == 'POST':
        contract.delete()
        messages.success(request, 'Contract deleted successfully!')
        return redirect('contract_list')
    return render(request, 'contract/contract_confirm_delete.html', {'contract': contract})

@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    user_contracts = UserContract.objects.filter(contract=contract).select_related('employee')

    logger.info(f"Viewing details for contract {contract.name} (ID: {pk})")
    logger.info(f"Found {user_contracts.count()} user contracts")

    return render(request, 'contract/contract_detail.html', {
        'contract': contract,
        'user_contracts': user_contracts,
    })
