<div class="timerdiv">
    {{message}}
        <br/>
        <span class="redirect" id="timerid"></span>
        <br/>
        секунд
</div>

<style type="text/css">
.redirect {
                border:0;
                margin-top: 5%;
                color: #F00;
                font-size: 30px;
                font-weight:700;
                text-align: center;
                }

.timerdiv { 
    /*width: 200px;
    background: #ccc;*/
    padding: 5px;
    /*padding-top: 30px;
        padding-right: 100px;*/
    border: 0; 
    float: right;
        text-align: center;
}
</style>

<script LANGUAGE="JavaScript">
<!--/ Начало скрипта
                /*var beep1 = new Audio("beep-1.mp3");
                var beep2 = new Audio("beep-2.mp3");*/
        var start=new Date();
        start = Date.parse(start)/1000;
        var counts = {{NUMBER_SEC_REDIRECT}};   <!--/ переменной присваивается число, определяющее время ожидания /-->
        function CountDown(){
                var now = new Date();
                now = Date.parse(now) / 1000;
                var x = parseInt(now - start, 10);
                document.getElementById("timerid").innerHTML = counts - x;
                                /*if ((counts - x) == 150) beep1.play();*/
                if (x < counts) {
                        timerID = setTimeout("CountDown()", 100)
                } else {
                        if (document.check) {
                            document.check.submit();
                        } else {
                                location.href={{NEXT_PAGE}}
                        }
                }
        }

//  Конец скрипта -->
<!--/ задержка, установлена по умолчанию (желательно не изменять) равна (100 милисекундам т.е. 1 секунде)
window.setTimeout('CountDown()',100);
-->
</script>


