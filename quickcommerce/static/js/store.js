

// Update the price range filter
$('#priceRange').on('input', function() {
    let value = $(this).val();
    $('#minPrice').val(`$0`);
    $('#maxPrice').val(`$${value}`);
  });
  // Mock logic: check if location is fetched from the server
  let locationFetchedFromServer = true; // change to true if the location is fetched

  $(document).ready(function () {
    // Check if the location is fetched and show accordingly
    if (locationFetchedFromServer) {
      $('#current-location').removeClass('d-none');
    } else {
      $('#location-select').removeClass('d-none');
    }

    // When location is selected, change ETA dynamically
    $('#location-select').on('change', function () {
      let selectedLocation = $(this).val();
      let eta = '-- min'; // default ETA

      switch (selectedLocation) {
        case 'pune':
          eta = '20 min';
          break;
        case 'mumbai':
          eta = '45 min';
          break;
        case 'delhi':
          eta = '60 min';
          break;
        default:
          eta = '-- min';
      }

      $('#eta-value').text(eta);
    });

    $('.wishlist-icon').on('click', function () {
      const icon = $(this);
      const productSlug = icon.data('product-slug');  // Assuming the product slug is stored as a data attribute
      const isActive = icon.hasClass('active');
      const url = isActive ? `/wishlist/remove/${productSlug}/` : `/wishlist/add/${productSlug}/`;  // Dynamic URL based on action
      const method = isActive ? 'DELETE' : 'POST';  // Use DELETE for removing, POST for adding
  
      // Toggle UI first for instant feedback
      icon.toggleClass('active');
      if (icon.hasClass('active')) {
          icon.removeClass('bi-heart').addClass('bi-heart-fill');  // Filled heart
      } else {
          icon.removeClass('bi-heart-fill').addClass('bi-heart');  // Outline heart
      }
  
      // AJAX request to add or remove the product from the wishlist
      $.ajax({
          url: url,
          method: method,
          data: {
              product_slug: productSlug,
              csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  // CSRF token for security
          },
          success: function (response) {
              console.log(response.status);  // Optional: You can add feedback or toast messages here
          },
          error: function (error) {
              console.error('Error:', error);
              // Revert UI if the request fails
              icon.toggleClass('active');
              if (icon.hasClass('active')) {
                  icon.removeClass('bi-heart').addClass('bi-heart-fill');  // Filled heart
              } else {
                  icon.removeClass('bi-heart-fill').addClass('bi-heart');  // Outline heart
              }
          }
      });
  });
  

  });