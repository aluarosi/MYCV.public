/* 
 * Main mycv.js file
 * Requires jQuery
 */

var mycv_config = {
    generatepassword_url: "/credentials/generate_password/"
}

var mycv = {

    ready: function() {
        mycv.bind_generatepassword();
        mycv.stateselector();
        mycv.help();
        prettyPrint();  //Prettify
    },
    bind_generatepassword: function() {
        $('#generatepassword').click(
            function(e) {
                e.preventDefault();
                //$(this).css('color','red');    
                var id = $('#request_id').attr('data-id');
                var url = mycv_config.generatepassword_url.concat(id).concat("/");
                $('#passwordvalue').load(
                    url
                );
            }
        );
    },
    stateselector: function() {
        /* Makes state selector drop-down to be automatic */
        $('select#stateselector').siblings('input.submit').hide();
        $('select#stateselector').change(
            function (e) {
                $(this).siblings('input.submit').trigger('click');
            }
        );
    },
    help: function() {
        $('.helped').each(
            function() {     
                $(this).hover( 
                    function() {
                        $(this).before(
                            '<span class="help">'+
                            $(this).attr('data-helptext') +
                            '</span>'
                        );
                    },
                    function() {
                        $('.help').remove();
                    }
                );
            }
        ); 
    },
    dummy: "Dummy"
}

$(document).ready(mycv.ready);

