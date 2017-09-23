function clickLike() {
  // Here, "this" is the button that the user clicked.
  var button = $(this);

  // Move through the DOM tree to find the "likes"
  // element that corresponds to the clicked button.

  // Look through parents of this to find .photo.
  var post = $(this).parents('.post');

  // Look inside photo to find .likes.
  var likes = $(post).find('.likes');

  // Get the URLsafe key from the button value.
  var urlsafeKey = $(button).val();

  // Send a POST request and handle the response.
  $.post('/like', {'post_key': urlsafeKey}, function(response) {
    // Update the number in the "like" element.
    $(likes).text(response);
  });
}

$('.post button').click(clickLike);
