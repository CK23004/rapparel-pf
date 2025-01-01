document.addEventListener('DOMContentLoaded', function() {
    const inventorySoftwareField = document.querySelector('#id_inventory_software');  // Get the inventory_software field
    const apiAccessTokenField = document.querySelector('#id_api_access_token'); // Get the api_access_token field
    const apiRefreshTokenField = document.querySelector('#id_api_refresh_token'); // Get the api_refresh_token field
    const apiTokenExpiryField = document.querySelector('#id_api_token_expiry');// Get the api_token_expiry field
    const apiClientIdField = document.querySelector('#id_api_client_id');  // Get the api_client_id field
    const apiClientSecretField = document.querySelector('#id_api_client_secret');// Get the api_client_secret field

    // Function to toggle API fields visibility based on inventory software field value
    function toggleApiFields() {
        if (inventorySoftwareField.value === 'excel') {
            // Hide API fields if 'Excel' is selected
            apiAccessTokenField.style.display = 'none';
            apiRefreshTokenField.style.display = 'none';
            apiTokenExpiryField.style.display = 'none';
            apiClientIdField.style.display = 'none';
            apiClientSecretField.style.display = 'none';
        } else {
            // Show API fields if other software is selected
            apiAccessTokenField.style.display = 'block';
            apiRefreshTokenField.style.display = 'block';
            apiTokenExpiryField.style.display = 'block';
            apiClientIdField.style.display = 'block';
            apiClientSecretField.style.display = 'block';
        }
    }

    // Attach event listener to inventory software field to detect changes
    inventorySoftwareField.addEventListener('change', toggleApiFields);

    // Initial run to toggle API fields on page load
    toggleApiFields();
});
