RFC2308の仕様の確認  

 
# SOAのTTLとminimumの関係性テスト
今までネガティブキャッシュの値は常にminimumの値を用いると勘違いしていましたが、  
RFC2308を読むと権威サーバもキャッシュサーバもSOAのTTLとminimumの小さい方を用いると書いてありました。    
今までの認識と異なり、にわかには信じがたい内容だったのでテストしてみました。    

<br />

## 検証環境  
Unbound 1.6.3  
NSD 4.1.15  

<br />

## 権威サーバのゾーンファイルのSOA TTLに30, minimumに15を指定した場合

#### 実行コマンド
dig @127.0.0.1 noexist.shutingrz.com.  

<br />

#### 権威サーバの応答
>   Authoritative nameservers     
>         shutingrz.com: type SOA, class IN, mname ns.shutingrz.com    
>             Name: shutingrz.com    
>             Type: SOA (Start Of a zone of Authority) (6)    
>             Class: IN (0x0001)    
>             Time to live: 15    
>             Data length: 33    
>             Primary name server: ns.shutingrz.com    
>             Responsible authority's mailbox: admin.shutingrz.com    
>             Serial Number: 20170101    
>             Refresh Interval: 3600 (1 hour)    
>             Retry Interval: 3600 (1 hour)    
>             Expire limit: 3600 (1 hour)    
>             Minimum TTL: 15 (15 seconds)    

NSDからのレスポンスをtsharkで見やすく表示したものです。  
ゾーンファイルにTTL:30, minimum:15 を書いても小さい値に揃えられます。 (仕様通り)    


<br />

#### キャッシュサーバの応答

> ;; AUTHORITY SECTION:    
> shutingrz.com.          15      IN      SOA     ns.shutingrz.com. admin.shutingrz.com. 20170101 3600 3600 3600 15    
 
NSDが小さい方に揃えているので当然両方15になっています。  
 
<br />

## 自作権威サーバでSOAに30, minimumに15を指定した場合

NSDを用いるとTTLが揃えられてしまうのでキャッシュサーバがRFC2308を満たしているか確認ができません。     
そのため、SOAとminimumの値が異なってもそのまま応答を返すスクリプトを作成して検証を行いました。     
スクリプトは、本リポジトリの soatest.py を参照してください。     

<br />

#### 権威サーバの応答
>    Authoritative nameservers    
>         shutingrz.com: type SOA, class IN, mname ns.shutingrz.com    
>             Name: shutingrz.com    
>             Type: SOA (Start Of a zone of Authority) (6)    
>             Class: IN (0x0001)    
>             Time to live: 30    
>             Data length: 33    
>             Primary name server: ns.shutingrz.com    
>             Responsible authority's mailbox: admin.shutingrz.com    
>             Serial Number: 20170101    
>             Refresh Interval: 3600 (1 hour)    
>             Retry Interval: 3600 (1 hour)    
>             Expire limit: 3600 (1 hour)    
>             Minimum TTL: 15 (15 seconds)    


自作権威サーバは、仕様に準拠せず TTL:30, minimum:15 を返しています。     

<br />

#### キャッシュサーバの応答

> ;; AUTHORITY SECTION:    
> shutingrz.com.          15      IN      SOA     ns.shutingrz.com. admin.shutingrz.com. 20170101 3600 3600 3600 15    

権威サーバからの応答が TTL:30, minimum:15 の場合でも、ちゃんと小さい15に揃えて表示されます。  

<br />

#### キャッシュサーバのキャッシュ情報

Unbound はキャッシュされる前のデータはそのままクライアントに返すという仕様らしく、  
実はキャッシュは異なるかもしれないため、念のためにダンプします。  

> \# unbound-control dump_cache    
> (中略)    
> shutingrz.com.  15      IN      SOA     ns.shutingrz.com. admin.shutingrz.com. 20170101 3600 3600 3600 15    

キャッシュの情報も小さい方の15に揃えられていました。  
 
<br />

## 結論
SOAのTTLとminimumが異なる値の場合には、ネガティブキャッシュのTTLは小さい方を用いるという仕様で間違いありません。    
よって、自分の今までの理解が間違っていることがわかりました。  

<br />

※NSDおよびUnbound以外の実装では異なる結果が得られる可能性があります。
