var alignments = null; // To be set later
var alignments2 = null; // To be set later
var tableDom = 
  '<"row"<"col-sm-12 col-md-6"B><"col-sm-12 col-md-3"l><"col-sm-12 col-md-3"f>>' +
  '<"row"<"col-sm-12"tr>>' +
  '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>';
window.addEventListener('DOMContentLoaded', (event) => {
  
});

var t = $('#table-spectra').DataTable({
  data: JSON.parse($('#data-spectra')[0].textContent),
  scrollX: true,
  columns: [
    {data: 'id', title: 'Spectra ID'},
    {data: 'strain_id', title: 'Strain ID'},
    {data: 'min_mass', title: 'Min mass'},
    {data: 'max_mass', title: 'Max mass'}
  ]
});
var t = $('#table-cspectra').DataTable({
  data: JSON.parse($('#data-cspectra')[0].textContent),
  scrollX: true,
  columns: [
    {data: 'id', title: 'Collapsed Spectra ID'},
    {data: 'strain_id', title: 'Strain ID'},
    {data: 'min_mass', title: 'Min mass'},
    {data: 'max_mass', title: 'Max mass'},
    {data: 'spectra_content', title: 'Spectra content'},
    {data: 'num_spectra', title: '# spectra'},
    {data: 'min_snr', title: 'Min SNR'},
    {data: 'peak_percent_presence', title: 'Peak % presence'},
    {data: 'tolerance', title: 'Bin peaks tolerance'},
    {data: 'generated_date', title: 'Generated'}
  ]
});
var t = $('#table-metadata').DataTable({
  data: JSON.parse($('#data-metadata')[0].textContent),
  scrollX: true,
  columns: [
    {data: 'id', title: 'Metadata ID'},
    {data: 'strain_id', title: 'Strain ID'},
    {data: 'genbank_accession', title: 'Genbank accession'},
    {data: 'ncbi_taxid', title: 'NCBI'},
    {data: 'cKingdom', title: 'Kingdom'},
    {data: 'cPhylum', title: 'Phylum'},
    {data: 'cClass', title: 'Class'},
    {data: 'cOrder', title: 'Order'},
    {data: 'cFamily', title: 'Family'},
    {data: 'cGenus', title: 'Genus'},
    {data: 'cSpecies', title: 'Species'},
    {data: 'cSubspecies', title: 'Subspecies'},
    {data: 'created_by__username', title: 'Created by'}
  ]
});

function noevent(e) {
  e.stopPropagation();
  e.preventDefault();
  return false;
}
var socket = new WebSocket('ws://' + location.host + '/ws/pollData');
socket.onopen = function(e){
  //console.log(e);
}
socket.onmessage = function(e) {
  $('#align-load')[0].disabled = false;
  $('#align-prefix')[0].disabled = false;
  
  console.log(e);
  var data = JSON.parse(e.data).data;
  console.log(data);
  
  // exact matches versus non-matches
  if (data.message == 'completed align') {
    $('#align-alert')
      .text('Showing only Metadata entries where the NCBI taxonomic ID is empty');
    $('#align1').css('display', '');
    $('#align2').css('display', '');
    $('#align-import').css('display', '');
    $('#align').css('display', '');
    
    if (data.data.result1.length > 0) {
      $('#align-import').on('click', alignImport);
      $('#align-import')[0].disabled = false;
      alignments = data.data.result1;
    } else {
      $('#align-import')[0].disabled = true;
    }
    
    var t = $('#align1').DataTable({
      data: data.data.result1,
      destroy: true, // https://datatables.net/manual/tech-notes/3
      columns: [
        {data: 'id', title: 'ID'},
        {data: 'strain_id', title: 'Strain ID'},
        //~ {data: 'strain_id__strain_id', title: 'Strain Name'},
        {data: 'exact_name', title: 'Name'},
        {data: 'exact_sciname', title: 'Scientific name'},
        {data: 'exact_txid', title: 'NCBI taxonomic ID'},
        {data: 'exact_txtype', title: 'Taxonomic rank'},
        {data: 'exact_parentname', title: 'Parent name'}
      ]
    });
    t.draw();
    var t2 = $('#align2').DataTable({
      data: data.data.result2,
      destroy: true, // https://datatables.net/manual/tech-notes/3
      dom: tableDom,
      buttons: [
        'selectAll',
        'selectNone',
        {
          text: 'Add selected Metadata',
          action: function (e, dt, button, config) {
            // for each selected row, get the database ID plus the selected option value
            var x = dt.rows({selected: true}).data().toArray();
            var y = dt.rows({selected: true}).nodes();
            var save = [];
            for (var i in x) {
              var s = y[i].getElementsByTagName('select');
              if (s.length == 0) continue; // no option
              save.push({
                exact_txid: s[0].options[s[0].selectedIndex].value,
                id: x[i].id
              })
            }
            saveAlignSelected(save);
            // removes selected
            dt.rows({selected: true}).remove().draw();
          }
        }
      ],
      language: {
        buttons: {
          selectAll: "Select all",
          selectNone: "Select none"
        }
      },
      columnDefs: [{
        orderable: false,
        className: 'select-checkbox',
        targets:   0
      }],
      select: {
        style: 'multi+shift',
        toggleable: true
      },
      columns: [
        {data: 'id', title: ' ',
          render: function(data, type) {
            return '';
          }
        },
        {data: 'partial_ids', title: 'Update ID',
          render: function(data, type) {
            if (!data || data.length == 0) return '';
            var d = [];
            for (var i in data) {
              d.push('<option value="' + i + '">' + i + '</option>');
            }
            return '<select onclick="javascript: noevent(event);">' +
              d.join() + '</select>';
          }
        },
        {data: 'id', title: 'ID'},
        {data: 'strain_id', title: 'Strain ID'},
        {data: 'partial_type', title: 'Search'},//,
        {data: 'partial', title: 'Result (includes up to two results)',
          render: function(data, type) {
            return data.split('|').join('<br>');
          }
        }
      ]
    });
    t.draw();
  }
  // 
  else if (data.message == 'align status') {
    $('#align-alert').text(data.data.status);
  }
  // 
  else if (data.message == 'completed save align') {
    $('#align-alert').text('Alignment updated!');
  }
  //
  else if (data.message == 'completed manual align') {
    $('#manual-align-import').css('display', '');
    $('#align3').css('display', '');
    $('#align4').css('display', '');
    $('#align-alert-manual').text('');
    $('#align-alert-manual').css('display', 'none');
    $('#manual-align-preview')[0].disabled = false;
    $('#manual1')[0].disabled = false;
    $('#manual2')[0].disabled = false;
    $('#manual3')[0].disabled = false;
    
    if (data.data.result1.length > 0) {
      $('#manual-align-import').on('click', alignImportManual);
      $('#manual-align-import')[0].disabled = false;
      alignments2 = data.data.result1;
    } else {
      $('#manual-align-import')[0].disabled = true;
    }
    
    var t = $('#align3').DataTable({
      data: data.data.result1,
      destroy: true, // https://datatables.net/manual/tech-notes/3
      columns: [
        {data: 'sid', title: 'Strain ID'},
        //~ {data: 'strain_id__strain_id', title: 'Strain Name'},
        {data: 'genus', title: 'Input genus'},
        {data: 'species', title: 'Input species'},
        {data: 'txid1', title: 'NCBI genus ID'},
        {data: 'txid2', title: 'NCBI species ID'}
      ]
    });
    t.draw();
    var t = $('#align4').DataTable({
      data: data.data.result2,
      destroy: true, // https://datatables.net/manual/tech-notes/3
      dom: tableDom,
      buttons: [
        'selectAll',
        'selectNone',
        {
          text: 'Add selected Metadata',
          action: function (e, dt, button, config) {
            // for each selected row, get the database ID plus the selected option value
            var x = dt.rows({selected: true}).data().toArray();
            var y = dt.rows({selected: true}).nodes();
            var save = [];
            for (var i in x) {
              var s = y[i].getElementsByTagName('select');
              if (s.length == 0) continue; // no option
              save.push({
                exact_txid: s[0].options[s[0].selectedIndex].value,
                id: x[i].id
              })
            }
            saveAlignSelected(save);
            // removes selected
            dt.rows({selected: true}).remove().draw();
          }
        }
      ],
      language: {
        buttons: {
          selectAll: "Select all",
          selectNone: "Select none"
        }
      },
      columnDefs: [{
        orderable: false,
        className: 'select-checkbox',
        targets:   0
      }],
      select: {
        style: 'multi+shift',
        toggleable: true
      },

      columns: [
        {data: 'id', title: ' ',
          render: function(data, type) {
            return '';
          }
        },
        {data: 'partial_ids', title: 'Update ID',
          render: function(data, type) {
            if (!data || data.length == 0) return '';
            var d = [];
            for (var i in data) {
              d.push('<option value="' + i + '">' + i + '</option>');
            }
            return '<select onclick="javascript: noevent(event);">' +
              d.join() + '</select>';
          }
        },

        {data: 'id', title: 'ID'},
        {data: 'sid', title: 'Strain ID'},
        {data: 'genus', title: 'Input genus'},
        {data: 'species', title: 'Input species'},
        {data: 'result', title: 'Match issue'},
        {data: 'txid1', title: 'NCBI genus ID'},
        {data: 'txid2', title: 'NCBI species',
          render: function(data, type) {
            return data.split('|').join('<br>');
          }
        }
      ]
    });
    t.draw();
  }
  // 
  else if (data.message == 'completed save manual align') {
    $('#align-alert-manual').css('display', '');
    $('#align-alert-manual').text('Alignment updated!');
    $('#manual-align-preview')[0].disabled = false;
    //~ $('#manual-align-import')[0].disabled = false;
    $('#manual1')[0].disabled = false;
    $('#manual2')[0].disabled = false;
    $('#manual3')[0].disabled = false;
  }
}
socket.onclose = function(e){
  //console.log(e);
}
function saveAlignSelected(rows) {
  socket.send(JSON.stringify({
    type: 'save align',
    library: library_id,
    alignments: rows
  }));
}
function alignImport() {
  $('#align-load')[0].disabled = true;
  $('#align-prefix')[0].disabled = true;
  $('#align-import')[0].disabled = true;
  $('#align-alert').text('Saving alignment...');
  socket.send(JSON.stringify({
    type: 'save align',
    library: library_id,
    alignments: alignments
  }));
}
function alignImportManual() {
  $('#manual-align-preview')[0].disabled = true;
  $('#manual-align-import')[0].disabled = true;
  $('#manual1')[0].disabled = true;
  $('#manual2')[0].disabled = true;
  $('#manual3')[0].disabled = true;
  $('#align-alert-manual').css('display', '');
  $('#align-alert-manual').text('Saving alignment...');
  socket.send(JSON.stringify({
    type: 'save manual align',
    library: library_id,
    alignments: alignments2
  }));
}
function manualAlign(btn) {
  btn.disabled = true;
  $('#manual1')[0].disabled = true;
  $('#manual2')[0].disabled = true;
  $('#manual3')[0].disabled = true;
  $('#align-alert-manual').css('display', '');
  $('#align-alert-manual').text('Loading alignment...');
  socket.send(JSON.stringify({
    type: 'manual_align',
    library: library_id,
    data: {
      strain_ids: $('#manual1')[0].value.trim(),
      genus: $('#manual2')[0].value.trim(),
      species: $('#manual3')[0].value.trim()
    }
  }));
}
function align(btn) {
  //~ btn.onclick = function() {}; // Disable
  btn.disabled = true;
  $('#align-prefix')[0].disabled = true;
  $('#align').css('display', 'none');
  $('#align-alert').css('display', '');
  $('#align-alert').text('Loading alignment...');
  $('#align-import').css('display', 'none');
  $('#align-prefix')[0].value = $('#align-prefix')[0].value.trim();
  socket.send(JSON.stringify({
    type: 'align',
    library: library_id,
    prefix: $('#align-prefix')[0].value
  }));
}
