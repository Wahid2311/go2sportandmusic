"""
Professional HTML Email Templates for TicketHouse
All emails follow a consistent professional design with proper formatting
"""

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail
import logging

logger = logging.getLogger(__name__)


class EmailTemplates:
    """Professional email template builder"""
    
    @staticmethod
    def get_header():
        """Get the email header with branding"""
        return """
        <div style="background-color: #1a5f3f; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">TicketHouse</h1>
            <p style="color: #e0e0e0; margin: 5px 0 0 0; font-size: 14px;">Your Premium Ticket Marketplace</p>
        </div>
        """
    
    @staticmethod
    def get_footer():
        """Get the email footer"""
        return """
        <div style="background-color: #f5f5f5; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px; margin: 0;">
                <strong>TicketHouse</strong> | Your Premium Ticket Marketplace<br>
                <a href="https://tickethouse.net" style="color: #1a5f3f; text-decoration: none;">Visit Our Website</a> | 
                <a href="https://tickethouse.net/support" style="color: #1a5f3f; text-decoration: none;">Support</a>
            </p>
            <p style="color: #999; font-size: 11px; margin: 10px 0 0 0;">
                © 2026 TicketHouse. All rights reserved.
            </p>
        </div>
        """
    
    @staticmethod
    def get_section_title(title):
        """Get a section title styling"""
        return f"""
        <h2 style="color: #1a5f3f; font-size: 18px; font-weight: bold; margin: 20px 0 15px 0; border-bottom: 2px solid #1a5f3f; padding-bottom: 10px;">
            {title}
        </h2>
        """
    
    @staticmethod
    def get_detail_row(label, value):
        """Get a detail row styling"""
        return f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                <strong style="color: #333;">{label}:</strong>
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                <span style="color: #666;">{value}</span>
            </td>
        </tr>
        """
    
    @staticmethod
    def payment_successful_buyer(order, ticket):
        """Email to buyer after successful payment"""
        details_html = ""
        for label, value in [
            ("Event", order.event_name),
            ("Date", order.event_date.strftime('%B %d, %Y')),
            ("Time", order.event_time.strftime('%I:%M %p')),
            ("Section", order.ticket_section),
            ("Row", order.ticket_row),
            ("Seats", ', '.join(order.ticket_seats)),
            ("Quantity", str(order.number_of_tickets)),
            ("Order ID", str(order.id)),
        ]:
            details_html += EmailTemplates.get_detail_row(label, value)
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                {EmailTemplates.get_header()}
                
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                        Dear <strong>{order.buyer.first_name or 'Valued Customer'}</strong>,
                    </p>
                    
                    <div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #2e7d32; font-weight: bold; margin: 0; font-size: 16px;">
                            ✓ Payment Successful!
                        </p>
                        <p style="color: #558b2f; margin: 5px 0 0 0; font-size: 14px;">
                            Your tickets have been secured. Thank you for your purchase!
                        </p>
                    </div>
                    
                    {EmailTemplates.get_section_title('Order Details')}
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        {details_html}
                    </table>
                    
                    <div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #e65100; font-weight: bold; margin: 0; font-size: 14px;">
                            📎 Ticket Attachments
                        </p>
                        <p style="color: #bf360c; margin: 5px 0 0 0; font-size: 13px;">
                            Your ticket PDFs are attached to this email. Please download and save them securely.
                        </p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                        You can view and manage your orders anytime by logging into your <strong>TicketHouse account</strong>. 
                        Your tickets are now ready for the event!
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://tickethouse.net/my-orders/" style="background-color: #1a5f3f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                            View My Orders
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; line-height: 1.6;">
                        <strong>Questions?</strong> Our support team is here to help. Contact us at 
                        <a href="mailto:support@tickethouse.net" style="color: #1a5f3f; text-decoration: none;">support@tickethouse.net</a>
                    </p>
                </div>
                
                {EmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def payment_successful_seller(order, ticket):
        """Email to seller when their ticket is sold"""
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                {EmailTemplates.get_header()}
                
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                        Dear <strong>{ticket.seller.first_name or 'Seller'}</strong>,
                    </p>
                    
                    <div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #1565c0; font-weight: bold; margin: 0; font-size: 16px;">
                            🎉 Your Ticket Has Been Sold!
                        </p>
                        <p style="color: #0d47a1; margin: 5px 0 0 0; font-size: 14px;">
                            Congratulations! A buyer has purchased your ticket.
                        </p>
                    </div>
                    
                    {EmailTemplates.get_section_title('Sale Details')}
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        {EmailTemplates.get_detail_row('Event', order.event_name)}
                        {EmailTemplates.get_detail_row('Ticket ID', str(ticket.ticket_id))}
                        {EmailTemplates.get_detail_row('Section', order.ticket_section)}
                        {EmailTemplates.get_detail_row('Quantity Sold', str(order.number_of_tickets))}
                        {EmailTemplates.get_detail_row('Order ID', str(order.id))}
                    </table>
                    
                    <div style="background-color: #f3e5f5; border-left: 4px solid #9c27b0; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #6a1b9a; font-weight: bold; margin: 0; font-size: 14px;">
                            📋 Next Steps
                        </p>
                        <p style="color: #4a148c; margin: 5px 0 0 0; font-size: 13px;">
                            Please ensure the ticket PDF is uploaded for verification. Payment will be processed after verification is complete.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://tickethouse.net/my-sales/" style="background-color: #1a5f3f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                            View My Sales
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; line-height: 1.6;">
                        <strong>Questions?</strong> Our support team is here to help. Contact us at 
                        <a href="mailto:support@tickethouse.net" style="color: #1a5f3f; text-decoration: none;">support@tickethouse.net</a>
                    </p>
                </div>
                
                {EmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def ticket_listing_confirmation(ticket, seller_email, marketplace_url):
        """Email to seller when ticket is listed"""
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                {EmailTemplates.get_header()}
                
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                        Hello,
                    </p>
                    
                    <div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #2e7d32; font-weight: bold; margin: 0; font-size: 16px;">
                            ✓ Ticket Listed Successfully!
                        </p>
                        <p style="color: #558b2f; margin: 5px 0 0 0; font-size: 14px;">
                            Your ticket is now live on the marketplace.
                        </p>
                    </div>
                    
                    {EmailTemplates.get_section_title('Listing Details')}
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        {EmailTemplates.get_detail_row('Event', ticket.event.name)}
                        {EmailTemplates.get_detail_row('Ticket ID', str(ticket.ticket_id))}
                        {EmailTemplates.get_detail_row('Section', ticket.section.name)}
                        {EmailTemplates.get_detail_row('Seats', ', '.join(ticket.seats))}
                        {EmailTemplates.get_detail_row('Price', f'£{ticket.sell_price:.2f}')}
                        {EmailTemplates.get_detail_row('Quantity', str(ticket.number_of_tickets))}
                    </table>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                        Your ticket is now visible to potential buyers on the TicketHouse marketplace. 
                        Buyers can view your listing and make purchases at any time.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{marketplace_url}" style="background-color: #1a5f3f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                            View Your Listing
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; line-height: 1.6;">
                        <strong>Questions?</strong> Our support team is here to help. Contact us at 
                        <a href="mailto:support@tickethouse.net" style="color: #1a5f3f; text-decoration: none;">support@tickethouse.net</a>
                    </p>
                </div>
                
                {EmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def payment_failed(order):
        """Email to buyer when payment fails"""
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                {EmailTemplates.get_header()}
                
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                        Dear <strong>{order.buyer.first_name or 'Valued Customer'}</strong>,
                    </p>
                    
                    <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #c62828; font-weight: bold; margin: 0; font-size: 16px;">
                            ✗ Payment Failed
                        </p>
                        <p style="color: #b71c1c; margin: 5px 0 0 0; font-size: 14px;">
                            Unfortunately, your payment could not be processed.
                        </p>
                    </div>
                    
                    {EmailTemplates.get_section_title('Order Information')}
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        {EmailTemplates.get_detail_row('Event', order.event_name)}
                        {EmailTemplates.get_detail_row('Order ID', str(order.id))}
                        {EmailTemplates.get_detail_row('Amount', f'£{order.amount:.2f}')}
                    </table>
                    
                    <div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #e65100; font-weight: bold; margin: 0; font-size: 14px;">
                            💡 What to Do Next
                        </p>
                        <ul style="color: #bf360c; margin: 10px 0 0 0; font-size: 13px; padding-left: 20px;">
                            <li>Check your card details and try again</li>
                            <li>Ensure you have sufficient funds</li>
                            <li>Contact your bank if the issue persists</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://tickethouse.net/my-orders/" style="background-color: #1a5f3f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                            Try Again
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; line-height: 1.6;">
                        <strong>Need Help?</strong> Our support team is ready to assist. Contact us at 
                        <a href="mailto:support@tickethouse.net" style="color: #1a5f3f; text-decoration: none;">support@tickethouse.net</a>
                    </p>
                </div>
                
                {EmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def event_created(event, admin_email):
        """Email to admin when event is created"""
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                {EmailTemplates.get_header()}
                
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                        Hello Admin,
                    </p>
                    
                    <div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #2e7d32; font-weight: bold; margin: 0; font-size: 16px;">
                            ✓ New Event Created
                        </p>
                        <p style="color: #558b2f; margin: 5px 0 0 0; font-size: 14px;">
                            A new event has been added to the system.
                        </p>
                    </div>
                    
                    {EmailTemplates.get_section_title('Event Details')}
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        {EmailTemplates.get_detail_row('Event ID', event.event_id)}
                        {EmailTemplates.get_detail_row('Event Name', event.name)}
                        {EmailTemplates.get_detail_row('Date', event.date.strftime('%B %d, %Y'))}
                        {EmailTemplates.get_detail_row('Time', event.time.strftime('%I:%M %p'))}
                        {EmailTemplates.get_detail_row('Stadium', event.stadium_name)}
                        {EmailTemplates.get_detail_row('Sections', str(event.sections.count()))}
                    </table>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                        The event is now active in the system and ready for ticket listings.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; line-height: 1.6;">
                        This is an automated notification from TicketHouse.
                    </p>
                </div>
                
                {EmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def send_html_email(subject, html_content, recipient_email, attachments=None):
        """Send HTML email with optional attachments"""
        try:
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            email.content_subtype = 'html'
            
            if attachments:
                for filename, content, content_type in attachments:
                    email.attach(filename, content, content_type)
            
            email.send()
            logger.info(f"Email sent successfully to {recipient_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
