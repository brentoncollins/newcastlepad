var time;
var frequency;
var duration;

function settimerFunction(){
if(((time.length < 6 && frequency.length < 2 && duration < 301))) {
    var joined = time + ',' + frequency + ',' + duration;

    document.getElementById('button1').style.visibility = 'visible';
    document.getElementById('button1').setAttribute('value', joined);
}

}

function timeFunction(time_of_day) {
    time = time_of_day;
    if (frequency == null){
        frequency = "<span class='red'> CHOOSE A FREQUENCY </span>"
    };
    if (duration == null){
        duration = "<span class='red'> CHOOSE A DURATION </span>"
    };
    document.querySelectorAll('input[type=submit]');
    document.getElementById('outputtext')
        .innerHTML = "<span class='status'>Run the timer at </span>" + time + " every " + frequency + " days for " + duration + " second(s)";
    settimerFunction()
}

function frequencyFunction(frequency_time) {
    frequency = frequency_time;
    if (time == null){
        time = "<span class='red'> CHOOSE A TIME </span>"
    };
    if (duration == null){
        duration = "<span class='red'> CHOOSE A DURATION </span>"
    };
    document.querySelectorAll('input[type=submit]');
    document.getElementById('outputtext')
        .innerHTML ="<span class='status'>Run the timer at </span>" + time + " every " + frequency + " days for " + duration + " second(s)";
    settimerFunction()
}

function durationFunction() {
    if (time == null){
        time = "<span class='red'> CHOOSE A TIME </span>"
    };
    if (frequency == null){
        frequency = "<span class='red'> CHOOSE A FREQUENCY </span>"
    };

    duration = document.getElementById('duration_text').value;
    if (duration > 300) {
        duration = "<span class='red'> CHOOSE A DURATION </span>";
        document.getElementById('outputtext').innerHTML = ""
        document.getElementById('error_output').innerHTML = "<span class='red'>The Maximum watering time is 5 minutes</span>";
        document.getElementById('outputtext').innerHTML ="<span class='output'>Run the timer at </span>" + time + " every " + frequency + " days for " + duration + " seconds";


    } else {document.getElementById('error_output').innerHTML = "";
            document.getElementById('outputtext').innerHTML ="<span class='status'>Run the timer at </span>" + time + " every " + frequency + " days for " + duration + " seconds";
            settimerFunction()


    }
    ;
}

function drop1Function() {
    document.getElementById("myDropdown1").classList.toggle("show");
}

function drop2Function() {
    document.getElementById("myDropdown2").classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matches('.dropbtn2')) {

        var dropdowns2 = document.getElementsByClassName("dropdown2-content");
        var i;
        for (i = 0; i < dropdowns2.length; i++) {
            var openDropdown2 = dropdowns2[i];
            if (openDropdown2.classList.contains('show')) {
                openDropdown2.classList.remove('show');
            }
        }

    }
    if (!event.target.matches('.dropbtn1')) {

        var dropdowns1 = document.getElementsByClassName("dropdown1-content");
        var x;

        for (x = 0; x < dropdowns1.length; x++) {
            var openDropdown1 = dropdowns1[x];
            if (openDropdown1.classList.contains('show')) {
                openDropdown1.classList.remove('show');
            }
        }

    }
}

