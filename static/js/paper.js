function expand_authors(id) {
  $('#author_' + id + '_short').addClass('d-none');
  $('#author_' + id + '_short').removeClass('d-inline');
  $('#author_' + id + '_long').addClass('d-inline');
  $('#author_' + id + '_long').removeClass('d-none');
}

function collapse_authors(id) {
  $('#author_' + id + '_short').addClass('d-inline');
  $('#author_' + id + '_short').removeClass('d-none');
  $('#author_' + id + '_long').addClass('d-none');
  $('#author_' + id + '_long').removeClass('d-inline');
}
  
function expand_abstract(id) {
  $('#abstract_' + id + '_short').addClass('d-none');
  $('#abstract_' + id + '_short').removeClass('d-inline');
  $('#abstract_' + id + '_long').addClass('d-inline');
  $('#abstract_' + id + '_long').removeClass('d-none');
}

function collapse_abstract(id) {
  $('#abstract_' + id + '_short').addClass('d-inline');
  $('#abstract_' + id + '_short').removeClass('d-none');
  $('#abstract_' + id + '_long').addClass('d-none');
  $('#abstract_' + id + '_long').removeClass('d-inline');
}

function expand_keywords(id) {
  $('#keyword_' + id + '_short').addClass('d-none');
  $('#keyword_' + id + '_short').removeClass('d-inline');
  $('#keyword_' + id + '_long').addClass('d-inline');
  $('#keyword_' + id + '_long').removeClass('d-none');
}

function collapse_keywords(id) {
  $('#keyword_' + id + '_short').addClass('d-inline');
  $('#keyword_' + id + '_short').removeClass('d-none');
  $('#keyword_' + id + '_long').addClass('d-none');
  $('#keyword_' + id + '_long').removeClass('d-inline');
}

function translate_title(paper_id, url, csrf_token) {
  if ($('#title_cn_' + paper_id).html().trim() !== '') {
    if ($('#title_cn_' + paper_id).hasClass('d-none')) {
      $('#title_cn_' + paper_id).addClass('d-block');
      $('#title_cn_' + paper_id).removeClass('d-none');
    } else {
      $('#title_cn_' + paper_id).addClass('d-none');
      $('#title_cn_' + paper_id).removeClass('d-block');
    }
  } else {
    $('#title_cn_' + paper_id).addClass('d-block');
    $('#title_cn_' + paper_id).removeClass('d-none');
    $('#title_cn_' + paper_id).html('<div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div>');

    $.ajax({
      url: url,
      type: 'POST',
      headers: { "X-CSRFToken": csrf_token },
      data: { paper_id: paper_id },
      success: function (data) {
        console.log(data)
        if (!data.success) {
          alert('Translate title failed!\n' + data.error);
        } else {
          $('#title_cn_' + paper_id).html(data.answer);
        }
      },
      error: function () {
        alert('An error occurred while processing your request.');
      }
    });
  }
}

function translate_abstract(paper_id, url, csrf_token) {
  if ($('#abstract_cn_' + paper_id).html().trim() !== '') {
    if ($('#abstract_cn_' + paper_id).hasClass('d-none')) {
      $('#abstract_cn_' + paper_id).addClass('d-block');
      $('#abstract_cn_' + paper_id).removeClass('d-none');
    } else {
      $('#abstract_cn_' + paper_id).addClass('d-none');
      $('#abstract_cn_' + paper_id).removeClass('d-block');
    }
  } else {
    $('#abstract_cn_' + paper_id).addClass('d-block');
    $('#abstract_cn_' + paper_id).removeClass('d-none');
    $('#abstract_cn_' + paper_id).html('<div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div>');

    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json',
      headers: { "X-CSRFToken": csrf_token },
      data: { paper_id: paper_id },
      success: function (data) {
        if (!data.success) {
          alert('Translate title failed!\n' + data.error);
        } else {
          $('#abstract_cn_' + paper_id).html(data.answer);
        }
      },
      error: function () {
        alert('An error occurred while processing your request.');
      }
    });
  }
}
