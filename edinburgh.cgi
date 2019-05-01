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
  my $title = 'Edinburgh Leisure Pool Programmes';
  say $q->header;
  say $q->start_html( { style => 'style.css',
                        title => $title } );
  say $q->h2( $title );
}

sub get_venues {
  my $base_url = 'http://www.edinburghleisure.co.uk';
  
  my $mech = WWW::Mechanize->new();
  $mech->get( $base_url . '/activities/swim' );
  
  my $tree = HTML::TreeBuilder->new();
  $tree->parse_content( $mech->content );
  
  my @table_divs = $tree->look_down(
    _tag => 'td',
  );

  my @venues = ();
  foreach my $div ( @table_divs ) {
    my @venuenames = $div->look_down( _tag => 'a' );
    
    #my $venuename = $venuenames[0]->as_text();
    my $venuename = $div->as_text();
    
    my $links_ref = $div->extract_links( 'a' );
    my $link = $base_url . $links_ref->[0]->[0];
    
    push @venues, {
      name => $venuename,
      url => $link,
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
  
  say $q->p( $q->a( { href => 'https://www.edinburghleisure.co.uk/activities/swim' }, 'Source page' ) );
  
  say $q->p( $q->small( "Completed in $time seconds." ) )
      . $q->end_html();
}
