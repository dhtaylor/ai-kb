USE [AcmeErp2019SalesHistoryArchive]
EXEC dbo.usp_GetOrderLines2019ByCustomerId @CustomerId
SELECT oh.OrderHeaderId2, ol.LineItemQty2019Adj FROM x
