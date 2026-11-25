// Power Query (M) load steps
let
    Src = Csv.Document(File.Contents("data\superstore.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Typed = Table.TransformColumnTypes(Table.PromoteHeaders(Src),
        {{"Order Date", type date}, {"Ship Date", type date}, {"Sales", type number},
         {"Profit", type number}, {"Discount", type number}, {"Quantity", Int64.Type}}),
    WithMargin = Table.AddColumn(Typed, "margin", each if [Sales] = 0 then null else [Profit] / [Sales], type number)
in
    WithMargin
