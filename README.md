# book-review-site
https://tims-book-worms.herokuapp.com  

A book review site for the Book Worms book club  
Uses Goodreads API to get ratings

To use as an API, send GET request to:  
/api/\<ISBN\>

Returns JSON:  
{  
&nbsp;&nbsp;&nbsp;&nbsp;"title": "The Very Hungry Caterpillar",  
&nbsp;&nbsp;&nbsp;&nbsp;"author": "Eric Carle",  
&nbsp;&nbsp;&nbsp;&nbsp;"year": 1969,  
&nbsp;&nbsp;&nbsp;&nbsp;"isbn": "0241003008",  
&nbsp;&nbsp;&nbsp;&nbsp;"review_count": 356697,  
&nbsp;&nbsp;&nbsp;&nbsp;"average_score": 4.29  
}
