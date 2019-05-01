#!/usr/bin/perl
use strict;
use warnings;

use 5.010;

use lib qw( /home/ardavey/perl5/lib/perl5 );

use WWW::Mechanize;
use HTML::TreeBuilder;
use Time::HiRes qw( gettimeofday tv_interval );

use CGI qw( std );

my $start = [ gettimeofday() ];
my $q = CGI->new();

my $venues = get_venues();
start_page();
print_venues( $venues );
my $time = tv_interval( $start, [ gettimeofday() ] );
end_page( $time );


sub start_page {
  my $title = 'Midlothian Pool Timetables';
  say $q->header;
  say $q->start_html( { style => 'style.css',
                        title => $title } );
  say $q->h2( $title );
}

sub get_venues {
  my $base_url = 'https://www.midlothian.gov.uk/';
  my $path = 'directory/3/leisure_centres_and_swimming_pools/category/9';
  
  my $mech = WWW::Mechanize->new();
  $mech->get( $base_url.$path );
  
  my $tree = HTML::TreeBuilder->new();
  $tree->parse_content( $mech->content );
  
  my @venue_links = $tree->look_down(
    _tag => 'a',
    href => qr!/swimming_pools$!,
  );

  my @venues = ();
  foreach my $link ( @venue_links ) {
    my $venuename = $link->as_text();
    
    my $link_url = $link->attr_get_i( 'href' );
    $mech->get( $base_url.$link_url );
    $tree = HTML::TreeBuilder->new();
    $tree->parse_content( $mech->content );
    my $pdf_url = $tree->look_down(
      _tag => 'a',
      href => qr/programme\.pdf/,
    )->attr_get_i( 'href' );
    
    push @venues, {
      name => $venuename,
      url => $pdf_url,
    };
  }
  
  return \@venues;
}

sub print_venues {
  my ( $venues ) = @_;
  
  say $q->start_ul();
  
  foreach my $venue ( @$venues ) {
    say $q->li(
        $q->img( { src => 'swim.gif',
                   width => 16,
                   height => 16,
                 } ),
        $q->a( { href => $venue->{url} },
                $venue->{name}
             )
    );
  }

  say $q->end_ul();
}

sub end_page {
  my ( $time ) = @_;
  
  say $q->p( $q->a( { href => 'https://www.midlothian.gov.uk/directory/3/leisure_centres_and_swimming_pools/category/9' }, 'Source page' ) );
  
  say $q->p( $q->small( "Completed in $time seconds." ) )
      . $q->end_html();
}

