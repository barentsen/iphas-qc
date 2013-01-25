debug = function (msg) { if (window.console != undefined) { console.log(msg); } }


function get_band() {
    return $('input:radio[name=band]:checked').val();
}

function set_band(button_id) {
    $('#'+button_id).attr('checked', true);
    $('#'+button_id).button("refresh");
    update();
}

function get_best() {
    return $('input:radio[name=best]:checked').val();
}

function set_field(field) {
    $('#field').val( field );
    update();
}

function get_field() {
    return $('#field').val();
}

function update() {
    field = get_field();
    band = get_band();
    debug('Change to '+field+' band '+band);

    url_base = "http://stri-cluster.herts.ac.uk/~gb/iphas-quicklook/";
    if (band == 'colour') {
        filename = field + '_small.jpg';
        filename_large = field + '.jpg'
    } else {
        filename = field + '_small_' + band + '.jpg';
        filename_large = field + '_' + band + '.jpg';
    }
    debug( filename );
    $('#ra').html( iphasqc[field]['ra'] );
    $('#dec').html( iphasqc[field]['dec'] );
    $('#l').html( iphasqc[field]['l'] );
    $('#b').html( iphasqc[field]['b'] );
    $('#qflag').html( iphasqc[field]['qflag'] );
    $('#problems').html( iphasqc[field]['problems'] );
    $("#image-box").html("<a href='"+url_base+filename_large+"'><img src='"+url_base+filename+"'/></a>");
}

function next_field() {
    field = get_field();
    // Does the user want only the best fields?
    if (get_best() == "true") {
        best = "False";
        while (best == "False") {
            field = iphasqc[field]['next'];
            best = iphasqc[field]['is_best'];
        }
    // User wants all field
    } else {
        field = iphasqc[field]['next'];
    }
    // Make the update
    set_field( field );
}

function prev_field() {
    field = get_field();
    // Does the user want only the best fields?
    if (get_best() == "true") {
        best = "False";
        while (best == "False") {
            field = iphasqc[field]['prev'];
            best = iphasqc[field]['is_best'];
        }
    // User wants all field
    } else {
        field = iphasqc[field]['prev'];
    }
    // Make the update
    set_field( field );
}


$(function() {
    $( "#band-box" )
        .buttonset()
        .change(function() {           
            update();
        });

    $( "#best-box" )
        .buttonset()        
        .change(function() {
            is_best = get_best();
            debug(is_best);
            if (is_best == "true") {
                debug('Setting autocomplete options to iphas_best')
                $("#field").autocomplete('option', 'source', iphas_best);
            } else {
                debug('Setting autocomplete options to iphas_all')
                $("#field").autocomplete('option', 'source', iphas_all);
            }
        });

    //Now you definitely have the cars so you can do the autocomplete
    $('#field').autocomplete({
        source: iphas_all,
        minLength: 3,
        focus: function( event, ui ) {
            $('#field').val( ui.item.value );
        },
        select: function( event, ui ) {
            set_field( ui.item.value );
            return false;
        }
    }); 

    $( "#bestonly" ).button();

        $( "#prev" ).button({
          text: false,
          icons: {
            primary: "ui-icon-seek-prev"
          }
        }).click(function() {
            prev_field();
        });

        $( "#next" ).button({
          text: false,
          icons: {
            primary: "ui-icon-seek-next"
          }
        }).click(function() {
            next_field();
        });


    $( "#accordion" ).accordion({
      event: "click hoverintent",
      heightStyle: "fill"
    });
  

     $(document).keydown(function(event) {
        debug('Handler for .keydown() called. - ' + event.keyCode);

        // Backspace = 8
        if (event.keyCode == 37) {
            prev_field();   
        // Space = 32
        } else if (event.keyCode == 39) {
            next_field(); 
        // Arrow up
        } else if (event.keyCode == 38) {
            switch ( get_band() ) {
                case 'colour': set_band('band-i'); break;
                case 'ha': set_band('band-colour'); break;
                case 'r': set_band('band-ha'); break;
                case 'i': set_band('band-r'); break;
            }
        // Arrow down
        } else if (event.keyCode == 40) {
        switch ( get_band() ) {
                case 'colour': set_band('band-ha'); break;
                case 'ha': set_band('band-r'); break;
                case 'r': set_band('band-i'); break;
                case 'i': set_band('band-colour'); break;
            }
        }
    });

    update();
});
