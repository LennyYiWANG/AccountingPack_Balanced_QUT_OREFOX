function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
    }
    //function to load invoice data
    function loadInvoiceData() {
    fetch('/invoicing/get_invoices/')
        .then(response => response.json())
        .then(data => {
            // Clear existing table data
            invoiceTable.clear().draw();
            // Populate DataTable with new data
            data.data.forEach((invoice) => {
                invoiceTable.row.add([
                    invoice.client,
                    invoice.date,
                    invoice.total_amount
                ]).draw();
            });
        })
        .catch(error => {
            console.error('Error fetching invoice data:', error);
        });
    }
    let invoiceTable;   
    $(document).ready(function () {
        let csrftoken = getCookie('csrftoken');
        invoiceTable = $('#invoice-table').DataTable();
        loadInvoiceData();
        $('#invoice-form').submit(function (e) {
            e.preventDefault();

            var formData = new FormData(this);
            for (var pair of formData.entries()) {
                console.log(pair[0]+ ', '+ pair[1]); 
            }

            fetch("/invoicing/create_invoice/", {
                method: "POST",
                body: formData,
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": csrftoken,

                },
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    loadInvoiceData();
                    // Add new row to DataTable
                    invoiceTable.row.add([
                        invoice.client,
                        invoice.date,
                        invoice.total_amount
                ]).draw();
                    $('#createInvoiceModal').modal('hide');
                    document.getElementById("invoice-form").reset(); 
                    // Possibly, maybe need to reload the DataTable here to show the new data
                }
                // Error Handling goes here if necessary
                else {
                // Handle errors
                console.log(data.errors);
                }
            });
        });
        $.ajax({
            url: '/invoicing/get_clients/',  // Adjust this to your actual URL
            type: 'GET',
            success: function(response) {
                    const data = response.data;
                    const clientSelect = $('#clientList');  // Replace 'id_client' with the actual ID of your dropdown element

                    data.forEach(function(client) {
                        const option = new Option(client.name, client.id);  // Replace 'name' and 'id' with the actual field names
                        clientSelect.append(option);
                });
            },
            error: function(error) {
            console.log('Error:', error);
            }
        });
        $("#add-client-form").submit(function(e){
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/invoicing/add_client/",
            data: $(this).serialize(),
                success: function(response){
                    // Update the client list dropdown if needed
                    $("#clientList").append(new Option(response.client_name, response.client_id));
                    // Close the add new client modal
                    $("#addClientModal").modal("hide");
                    document.getElementById("add-client-form").reset();
                }
            });
        });
        let parentModal;

        // When 'Add Client' modal is about to be shown
        $('#addClientModal').on('show.bs.modal', function () {
            // Hide the parent modal
            parentModal = $('#createInvoiceModal');
            parentModal.modal('hide');
        });

        // When 'Add Client' modal is hidden
        $('#addClientModal').on('hidden.bs.modal', function () {
            // Show the parent modal again
            if (parentModal) {
                parentModal.modal('show');
            }
        });
        // Event Listener for the green button
        $('#create-invoice-button').click(function () {
        $('#createInvoiceModal').modal('show'); // Open the modal
        });
    })
    document.addEventListener('DOMContentLoaded', function() {
        const selectElement = document.getElementById('paymentTermsSelect');
        
        fetch('/invoicing/get_payment_terms/')
            .then(response => response.json())
            .then(data => {
                data.forEach(function(option) {
                    const optElement = document.createElement('option');
                    optElement.value = option.value;
                    optElement.textContent = option.display;
                    selectElement.appendChild(optElement);
                });
            })
            .catch(error => console.error('There was a problem:', error));
    });
    document.addEventListener('DOMContentLoaded', function() {
        const selectElement = document.getElementById('stateSelect');
        
        fetch('/invoicing/get_states/')
            .then(response => response.json())
            .then(data => {
                data.forEach(function(option) {
                    const optElement = document.createElement('option');
                    optElement.value = option.value;
                    optElement.textContent = option.display;
                    selectElement.appendChild(optElement);
                });
            })
            .catch(error => console.error('There was a problem:', error));
    });
