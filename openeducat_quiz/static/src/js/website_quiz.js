/** @odoo-module **/

    import { jsonrpc } from "@web/core/network/rpc_service";
    $(document).ready(function () {
        var tmp_local_storage={};
        tmp_local_storage.checked_boxes={};
        tmp_local_storage.current_que_id = null;

        var exam_id = $("input[name='ExamID']").val();

        if(exam_id !== undefined){
            jsonrpc("/quiz/configuration", {result_id:exam_id})
                .then(function(configure_data) {
                    if(configure_data.single_que){
                        // enable first question of grid
                        if(configure_data.que_required == 1){
                            var que_grid=$(".que_grid");
                            que_grid.css({
                                'pointer-events': 'none',
                                'cursor': 'default'
                            });
                            $(que_grid[0]).removeAttr('style');
                        }

                        //Reset quiz data while refresh
                        if (localStorage.getItem("quiz") !== null) {
                            tmp_local_storage = JSON.parse(window.localStorage.getItem("quiz"));
                            for(var i in tmp_local_storage.checked_boxes){
                                $('#'+tmp_local_storage.checked_boxes[i]).attr('checked','true');
                                var que_id = $("input[name='"+i+"']").parent().attr('index-id')
                                $("div[grid-index-id='"+ que_id +"']").addClass('que_answered');

                                if(configure_data.prev_readonly == 1){
                                    var radios = $("input[name='"+ i +"']")
                                    for (var i = 0; i< radios.length;  i++){
                                        radios[i].disabled = true;
                                    }
                                }

                                if(configure_data.que_required == 1){
                                    $("div[grid-index-id='"+ que_id +"']").removeAttr('style');
                                }
                            }
                            if(tmp_local_storage.current_que_id !== undefined){
                                $('.question').addClass('que_hide').removeClass('que_show');
                                $("div[index-id='"+ tmp_local_storage.current_que_id +"']").addClass('que_show');
                                $('.que_grid').removeClass('que_active');
                                $("div[grid-index-id='"+ tmp_local_storage.current_que_id +"']").addClass('que_active');
                            }
                        }

                        //remove prev button and disable question grid
                        if(configure_data.prev_allow == 0){
                            var que_grid=$(".que_grid");
                                que_grid.css({
                                    'pointer-events': 'none',
                                    'cursor': 'default'
                                });
//                            $(".que_grid").removeAttr('style');
                        }else{
                            $('.quiz_prv').remove();
                        }

                        //go next question and checking all configuration
                        $(document).on('click',".quiz_nxt, .quiz_finish",function(e){
                            var index_id = $('.que_show').attr('index-id');
                            var radio_grp= $("div[index-id='"+index_id+"']").find("input[type='radio']");
                            var radio_grp_name = $(radio_grp[0]).attr('name');
                            var next_id = $(this).attr('next-id');

                            if(configure_data.que_required == 1){
                                if ($("input[name='"+ radio_grp_name +"']:checked").length > 0) {
                                    change_que(next_id);
                                    $('#quiz_err_info').html('');
                                    $("div[grid-index-id='"+ index_id +"']").addClass('que_answered');
                                    $("div[grid-index-id='"+ index_id +"']").removeAttr('style');
                                    tmp_local_storage.checked_boxes[radio_grp_name] = $("input[name='"+ radio_grp_name +"']:checked").attr('id');
                                    tmp_local_storage.current_que_id=next_id;
                                }else{
                                    $('#quiz_err_info').html('<div class="alert alert-danger">'+
                                                                '<strong>Error!</strong> Answer is required '+
                                                            '</div>');
                                    return false;
                                }
                            }else{
                                if ($("input[name='"+ radio_grp_name +"']:checked").length > 0) {
                                    $("div[grid-index-id='"+ index_id +"']").addClass('que_answered');
                                }
                                var  next_id = $(this).attr('next-id');
                                change_que(next_id);
                                tmp_local_storage.checked_boxes[radio_grp_name] = $("input[name='"+ radio_grp_name +"']:checked").attr('id');
                                tmp_local_storage.current_que_id=next_id;
                            }

                            if(configure_data.prev_readonly == 1){
                                if ($("input[name='"+ radio_grp_name +"']:checked").length > 0) {
                                    $("div[grid-index-id='"+ index_id +"']").addClass('que_answered');
                                    var radios = $("input[name='"+ radio_grp_name +"']")
                                    for (var i = 0; i< radios.length;  i++){
                                        radios[i].disabled = true;
                                    }
                                }
                            }
                            if(configure_data.prev_allow == 0){
                                var que_grid=$(".que_grid");
                                que_grid.css({
                                    'pointer-events': 'none',
                                    'cursor': 'default'
                                });
                            }
                            window.localStorage.setItem("quiz", JSON.stringify(tmp_local_storage));

                            if($(this).attr('class').indexOf('quiz_finish') >=0){
                                delete localStorage["quiz"];
                                $("input[type='radio']").removeAttr('disabled');
                                $('#form_quiz').submit();
                            }
                        });

                        //perform prev question
                        $(document).on('click','.quiz_prv',function(e){
                            $('#quiz_err_info').html('');
                            var  prev_id = $(this).attr('prev-id');
                            change_que(prev_id);
                        });

                        //change question throgh grid
                        $('.que_grid').on('click',function(e){
                            var que_id = $(this).attr('grid-index-id');

                            var index_id = $('.que_active').attr('grid-index-id');
                            var radio_grp= $("div[index-id='"+index_id+"']").find("input[type='radio']");
                            var radio_grp_name = $(radio_grp[0]).attr('name');
                            if ($("input[name='"+ radio_grp_name +"']:checked").length > 0) {
                                $("div[grid-index-id='"+ index_id +"']").addClass('que_answered');
                                tmp_local_storage.checked_boxes[radio_grp_name] = $("input[name='"+ radio_grp_name +"']:checked").attr('id');
                                window.localStorage.setItem("quiz", JSON.stringify(tmp_local_storage));
                            }

                            $('.que_grid').removeClass('que_active');
                            $(this).addClass('que_active');
                            change_que(que_id);
                            tmp_local_storage.current_que_id=que_id;
                        });
                    }else{
                        if (localStorage.getItem("quiz") !== null){
                            tmp_local_storage = JSON.parse(window.localStorage.getItem("quiz"));
                            for(var i in tmp_local_storage.checked_boxes){
                                $('#'+tmp_local_storage.checked_boxes[i]).attr('checked','true');
                                if(configure_data.prev_readonly == 1){
                                    var radio_grp = $('#'+tmp_local_storage.checked_boxes[i]).attr('name');
                                    if ($("input[name='"+ radio_grp +"']:checked").length > 0) {
                                        var radios = $("input[name='"+ radio_grp +"']")
                                        for (var i = 0; i< radios.length; i++){
                                            radios[i].disabled = true;
                                        }
                                    }
                                }
                            }
                        }

                        if(configure_data.que_required == 1){
                            $("input[type='radio']").attr('required',true);
                        }

                        $("input[type='radio']").click(function(e){
                            var radio_grp = $(this).attr('name');
                            if(configure_data.prev_readonly == 1){
                                if ($("input[name='"+ radio_grp +"']:checked").length > 0) {
                                    var radios = $("input[name='"+ radio_grp +"']")
                                    for (var i = 0; i< radios.length; i++){
                                        radios[i].disabled = true;
                                    }
                                }
                            }
                            tmp_local_storage.checked_boxes[radio_grp] = $(this).attr('id');
                            window.localStorage.setItem("quiz", JSON.stringify(tmp_local_storage));
                        });

                        $(document).on('click',".quiz_finish",function(e){
                            delete localStorage['quiz']
                            $("input[type='radio']").removeAttr('disabled');
                            $('#form_quiz').submit();
                        });
                    }
                });

            function change_que(change_id){
                var  index_id = $('.que_show').attr('index-id');
                $("div[index-id='"+index_id+"']").addClass('que_hide').removeClass('que_show');
                $("div[index-id='"+change_id+"']").addClass('que_show').removeClass('que_hide');
                // for grid
                $("div[grid-index-id='"+ index_id +"']").removeClass('que_active');
                $("div[grid-index-id='"+ change_id +"']").addClass('que_active');
            }
        }
    });

