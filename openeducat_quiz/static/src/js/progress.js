$(document).ready(function () {
    progress($('.progress-value').text(), $('#progressBar'));
    function roundDecimal(value, decimals) {
        return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
    }
    function progress(percent, $element) {
        var percent = roundDecimal(percent, 2);
        var progressBarWidth = percent * $element.width() / 100;
        $element.find('div').animate({ width: progressBarWidth }, 1200).html(percent + "% ");
    }
});