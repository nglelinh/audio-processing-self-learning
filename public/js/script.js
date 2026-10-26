(function(document) {
  var toggle = document.querySelector('.sidebar-toggle');
  var sidebar = document.querySelector('#sidebar');
  var checkbox = document.querySelector('#sidebar-checkbox');

  if (window.innerWidth > 1480)
    checkbox.checked = true;

  document.addEventListener('click', function(e) {
    var target = e.target;

    if(!checkbox.checked ||
       sidebar.contains(target) ||
       (target === checkbox || target === toggle)) return;

    checkbox.checked = false;
  }, false);

  // A link inside <summary> should navigate. Stop the click before it toggles
  // the disclosure (some browsers activate <summary> even when the target is a link).
  var chapterLinks = sidebar.querySelectorAll('.sidebar-chapter-link');
  for (var i = 0; i < chapterLinks.length; i++) {
    chapterLinks[i].addEventListener('click', function(e) {
      e.stopPropagation();
    });
  }
})(document);
