$(document).ready(function() {
    var waitforelement = function() {
        if (document.getElementById("top-html").classList.contains("updating-collapsible")) {
            setTimeout(waitforelement, 10);
        } else {
            var targetElement = document.getElementById(origLink.split("#")[1]);
            var doc = document.documentElement;
            var top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
            var goto = top + targetElement.getBoundingClientRect().top - 20.5;
            var stickyHeaderNav = document.getElementById("sticky-header-nav");
            if (stickyHeaderNav != null) {
                goto = goto - stickyHeaderNav.getBoundingClientRect().height;
            }
            if (goto < 0) {
                goto = 0;
            }
            window.scrollTo(0, goto);
        }
    }
    var opencollapse = function() {
        if (document.getElementById("top-html").classList.contains("updating-collapsible")) {
            setTimeout(opencollapse, 10);
            return;
        }
        origLink = window.location.href;
        var linkSplit = window.location.href.split("#");
        if (linkSplit.length <= 1) {
            return;
        }
        var targetElement = document.getElementById(linkSplit[1]);
        if (targetElement == null) {
            window.location.href = linkSplit[0];
        }
        var targetID = linkSplit[1];
        var targetElement = document.getElementById(targetID);
        var toClickOuter = null
        while (targetElement != null && targetElement.parentElement != null) {
            if (targetElement.parentElement.classList.contains("list-collapsible")) {
                if (targetElement.parentElement.classList.contains("active") == false) {
                    if (targetElement.parentElement.children[0].classList.contains("collapsible-header")) {
                        toClickOuter = targetElement.parentElement.children[0];
                    }
                }
            }
            targetElement = targetElement.parentElement;
        }
        if (toClickOuter != null) {
            toClickOuter.parentElement.children[1].classList.add("instant-update");
            toClickOuter.click();
            setTimeout(opencollapse, 10);
            toClickOuter.parentElement.children[1].classList.remove("instant-update");
            return;
        }
        setTimeout(waitforelement, 10);
    }
    opencollapse();
});

function opencollapsewithlinkaddress(LinkElement, Pre, Address) {
    var currentHref = window.location.href.split("#")[0]
    if (currentHref.includes('/')) {
        currentHref = currentHref.split('/');
        currentHref = currentHref[currentHref.length - 1];
    }
    if (Address.split("#")[0] != currentHref) {
        window.location.href = Address;
        return false
    }
    var targetID = Address.split("#")[1];
    var targetElement = document.getElementById(targetID);
    if (targetElement == null) {
        return false
    }
    while (targetElement != null && targetElement.parentElement != null) {
        if (targetElement.parentElement.classList.contains("list-collapsible")) {
            if (targetElement.parentElement.classList.contains("active") == false) {
                if (targetElement.parentElement.children[0].classList.contains("collapsible-header")) {
                    targetElement.classList.add("instant-update");
                    targetElement.parentElement.children[0].click()
                    targetElement.classList.remove("instant-update");
                }
            }
        }
        targetElement = targetElement.parentElement;
    }
    if (Pre == true) {
        var gotoLinkOnceUpdatingCollapsibleIsDone = function() {
            if (document.getElementById("top-html").classList.contains("updating-collapsible")) {
                setTimeout(gotoLinkOnceUpdatingCollapsibleIsDone, 33);
            } else {
                var targetElement = document.getElementById(targetID);
                var doc = document.documentElement;
                var top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
                var goto = top + targetElement.getBoundingClientRect().top - 20.5;
                var stickyHeaderNav = document.getElementById("sticky-header-nav");
                if (stickyHeaderNav != null) {
                    goto = goto - stickyHeaderNav.getBoundingClientRect().height;
                }
                if (goto < 0) {
                    goto = 0;
                }
                window.scrollTo(0, goto);
            }
        }
        setTimeout(gotoLinkOnceUpdatingCollapsibleIsDone, 33);
    }
    return false;
}

$(document).ready(function() {
    document.addEventListener("keydown", function(e) {
        if (e.ctrlKey && e.key == 'f') {
            var CollapsiblesToOpen = document.getElementsByClassName('collapsible-body');
            for (let i = 0; i < CollapsiblesToOpen.length; i++) {
                if (CollapsiblesToOpen[i].parentElement.classList.contains('active') == false) {
                    CollapsiblesToOpen[i].classList.add("dont-close-others");
                    CollapsiblesToOpen[i].classList.add("instant-update");
                    CollapsiblesToOpen[i].parentElement.children[0].click()
                    CollapsiblesToOpen[i].classList.remove("instant-update");
                    CollapsiblesToOpen[i].classList.remove("dont-close-others");
                }
            }
            if (document.getElementById("top-html").classList.contains("expand-all") == false) {
                document.getElementById("top-html").classList.add("expand-all");
            }
            window.scrollTo(0, 0);
        }
    });
})

let slideIndex = [];

function initSlides(tagNumber) {
    while (slideIndex.length <= tagNumber) {
        slideIndex.push(0);
        showSlides(slideIndex.length - 1);
    }
}

function plusSlides(tagNumber, direction) {
    slideIndex[tagNumber] += direction
    showSlides(tagNumber);
}

function showSlides(no) {
    let targetSlideShowClass = "slideshow-container-instance" + no;
    let i, j;
    let x = document.getElementsByClassName(targetSlideShowClass);
    for (i = 0; i < x.length; i++) {
        let xSlides = x[i].getElementsByClassName("slide");
        if (slideIndex[no] >= xSlides.length) { slideIndex[no] = 0 }
        if (slideIndex[no] < 0) { slideIndex[no] = xSlides.length - 1 }
        for (j = 0; j < xSlides.length; j++) {
            xSlides[j].style.display = "none";
        }
        xSlides[slideIndex[no]].style.display = "block";
        let xSlideStatus = x[i].getElementsByClassName("slide-status");
        xSlideStatus[0].textContent = "Slide: " + (1 + slideIndex[no]) + " / " + xSlides.length;
    }
}