$(document).ready(function () {







  
    // Mock location input behavior
    $('#detect-location-btn').on('click', function () {
      $('#location-input').addClass('d-none'); // Hide the input
      $('#location-select').removeClass('d-none'); // Show the select box
    });
        
          $('#detect-location-btn-desktop').on('click', function () {
      $('#location-input-desktop').addClass('d-none'); // Hide the input
      $('#location-select-desktop').removeClass('d-none'); // Show the select box
    });
  
    // Check if the device is mobile
    function isMobileDevice() {
      return $(window).width() <= 768; // Check if the screen width is 768px or smaller
    }
  
    if (isMobileDevice()) {
      $('#bottom-nav').css('display', 'flex');
      $('#mobile-header').css('display', 'flex');
    }
  
    // Hide arrows if the total width of items doesn't exceed the container's width
    function hideArrowsIfNecessary(carousel, prevButton, nextButton) {
      const items = $(carousel).children();
      const totalItemsWidth = items.toArray().reduce((total, item) => {
        const marginRight = parseInt($(item).css('margin-right'), 10) || 0;
        return total + $(item).outerWidth() + marginRight;
      }, 0);
      const containerWidth = $(carousel).outerWidth();
  
      if (totalItemsWidth <= containerWidth) {
        $(prevButton).hide();
        $(nextButton).hide();
      } else {
        $(prevButton).show();
        $(nextButton).show();
      }
    }
  
    // Add scroll behavior for arrows
    function setupScrolling(carousel, prevButton, nextButton) {
      $(nextButton).on('click', function () {
        $(carousel).animate({ scrollLeft: '+=300' }, 300);
      });
  
      $(prevButton).on('click', function () {
        $(carousel).animate({ scrollLeft: '-=300' }, 300);
      });
    }
  
    // Category Carousel Setup
    const categoryCarousel = '#categoryCarousel';
    const prevCategoryButton = '#prev-category';
    const nextCategoryButton = '#next-category';
  
    hideArrowsIfNecessary(categoryCarousel, prevCategoryButton, nextCategoryButton);
    setupScrolling(categoryCarousel, prevCategoryButton, nextCategoryButton);
  
    // Brand Carousel Setup
    const brandCarousel = '#brandCarousel';
    const prevBrandButton = '#prev-brand';
    const nextBrandButton = '#next-brand';
  
    hideArrowsIfNecessary(brandCarousel, prevBrandButton, nextBrandButton);
    setupScrolling(brandCarousel, prevBrandButton, nextBrandButton);
  
    // Re-check on window resize to handle responsive layouts
    $(window).on('resize', function () {
      hideArrowsIfNecessary(categoryCarousel, prevCategoryButton, nextCategoryButton);
      hideArrowsIfNecessary(brandCarousel, prevBrandButton, nextBrandButton);
    });
  
    // // Search Input Fetching Logic
    // $('#search-bar').on('input', function () {
    //   const query = $(this).val();
  
    //   if (query.length >= 2) {  // Only send request if more than 2 characters
    //     $.ajax({
    //       url: `/search?q=${query}`,
    //       method: 'GET',
    //       dataType: 'json',
    //       success: function (data) {
    //         console.log(data);  // Handle the search results (e.g., show suggestions in a dropdown)
    //       },
    //       error: function (error) {
    //         console.error('Error:', error);
    //       }
    //     });
    //   }
    // });
  
    
  });
  