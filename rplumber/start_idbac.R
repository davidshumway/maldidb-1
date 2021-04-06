# Start an IDBac server
print("start idbac")

# crashes with error:
# "Warning: Error in <Anonymous>: error in evaluating the argument
# 'pool' in selecting a method for function 'poolCheckout':"
x <- shiny::shinyApp(
  ui = IDBacApp::app_ui(),
  server = IDBacApp::app_server,
  options = list(port=7125, host="0.0.0.0", quiet=TRUE)
)
print(x)


