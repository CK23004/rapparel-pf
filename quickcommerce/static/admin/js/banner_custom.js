document.addEventListener('DOMContentLoaded', function() {
    const placeField = document.querySelector('#id_place');  // Get the place field
    const taglineField = document.querySelector('#id_tagline').closest('.form-row');// Get the tagline  field
    const linkField = document.querySelector('#id_link').closest('.form-row');
    const buttonTextField = document.querySelector('#id_button_text').closest('.form-row');  // Get the button_text field
    const buttonLinkField = document.querySelector('#id_button_link').closest('.form-row');  // Get the button_link field

    // Function to toggle visibility based on place field value
    function toggleFields() {
        if (placeField.value === 'primary') {
            // Show button_text and button_link for main banner
            buttonTextField.style.display = 'block';
            buttonLinkField.style.display = 'block';
            taglineField.style.display = 'block';
            linkField.style.display = 'none';

        } else {
            // Hide button_text and button_link for carousel banners
            buttonTextField.style.display = 'none';
            buttonLinkField.style.display = 'none';
            taglineField.style.display = 'none';
            linkField.style.display = 'block';

        }
    }

    // Attach event listener to place field to detect change
    placeField.addEventListener('change', toggleFields);

    // Initial run to toggle fields on page load
    toggleFields();
});
