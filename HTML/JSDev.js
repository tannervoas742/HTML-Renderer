//Sticky listener. Doesnt work with absolute position though
$(document).ready(function() {
    var elementsToObserve = document.getElementsByClassName("collapsible-header");
    observer = new IntersectionObserver(
        ([e]) => e.target.classList.toggle("sticky-position-mode", e.intersectionRatio < 1), {
            threshold: [1]
        }
    );
    for (let i = 0; i < elementsToObserve.length; i++) {
        observer.observe(elementsToObserve[i]);
    }
});

$(document).ready(function() {
    setTimeout(function() {
        scroll(0, 0);
    }, 30);
    var origLink = window.location.href;
    var linkSplit = window.location.href.split("#");
    if (linkSplit.length <= 1) {
        return;
    }
    var targetID = linkSplit[1];
    targetElement = document.getElementById(targetID);
    while (targetElement != null && targetElement.parentElement != null) {
        if (targetElement.parentElement.classList.contains("list-collapsible")) {
            if (targetElement.parentElement.classList.contains("active") == false) {
                if (targetElement.parentElement.children[0].classList.contains("collapsible-header")) {
                    targetElement.parentElement.children[0].click()
                }
            }
        }
        targetElement = targetElement.parentElement;
    }
    setTimeout(function() {
        window.location.href = origLink;
    }, 1000);
});



function countParents(Element) {
    var count = 0;
    var targetElement = Element;
    while (targetElement != null) {
        targetElement = targetElement.parentElement;
        count = count + 1;
    }
    return count;
}

function stickyCollapseToTop() {
    var headersToCheck = document.getElementsByClassName("collapsible-header-open");

    for (let i = 0; i < headersToCheck.length; i++) {
        headersToCheck[i].style["z-index"] = countParents(headersToCheck[i]);
        if (headersToCheck[i].getBoundingClientRect().top < 1) {
            if (headersToCheck[i].classList.contains("sticky-position-mode") == false) {
                headersToCheck[i].classList.add("sticky-position-mode")
                    //headersToCheck[i].style["margin-left"] = -1 * headersToCheck[i].getBoundingClientRect().x;
                    //headersToCheck[i].style["margin-right"] = headersToCheck[i].style["margin-left"];

            }
        } else {
            if (headersToCheck[i].classList.contains("sticky-position-mode") == true) {
                headersToCheck[i].classList.remove("sticky-position-mode")
                    //headersToCheck[i].style["margin-left"] = "";
                    //headersToCheck[i].style["margin-right"] = "";
            }
        }
    }
}

function gotoCollapseElement(Element) {


    setTimeout(function() {
        stickyCollapseToTop();
        setTimeout(function() {
            var doc1 = document.documentElement;
            var top1 = (window.pageYOffset || doc1.scrollTop) - (doc1.clientTop || 0);
            window.scroll(0, top1 + Element.target.getBoundingClientRect().top);
            setTimeout(function() {
                var doc2 = document.documentElement;
                var top2 = (window.pageYOffset || doc2.scrollTop) - (doc2.clientTop || 0);

                window.scroll(0, top2 + Element.target.getBoundingClientRect().top);
            }, 100);
        }, 100);
    }, 100);

}

$(document).ready(function() {
    var collapsibleHeaders = document.querySelectorAll('.collapsible-header');

    collapsibleHeaders.forEach(collapsible => {
        collapsible.addEventListener('click', gotoCollapseElement);
    });
});

$(window).scroll(stickyCollapseToTop);

function opencollapsewithlinkaddress(Pre, Address) {
    var targetID = Address.split("#")[1];
    targetElement = document.getElementById(targetID);
    while (targetElement != null && targetElement.parentElement != null) {
        if (targetElement.parentElement.classList.contains("list-collapsible")) {
            if (targetElement.parentElement.classList.contains("active") == false) {
                if (targetElement.parentElement.children[0].classList.contains("collapsible-header")) {
                    targetElement.parentElement.children[0].click()
                }
            }
        }
        targetElement = targetElement.parentElement;
    }
    if (Pre == true) {
        setTimeout(function() {
            window.location.href = Address;
        }, 1000);
    }
    return false;
}