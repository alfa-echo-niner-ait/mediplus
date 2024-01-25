$(document).ready(function () {

    $("#logLi").click(function () { 
        $(this).toggleClass("bg-smint");
        $("#regLi").toggleClass("bg-smint");
    });

    $("#regLi").click(function () { 
        $(this).toggleClass("bg-smint");
        $("#logLi").toggleClass("bg-smint");
    });
});