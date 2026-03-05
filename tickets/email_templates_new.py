"""
STUNNING Professional HTML Email Templates for TicketHouse
Modern, exciting design with proper branding, logo, and beautiful layouts
"""

from django.conf import settings
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)


class ProfessionalEmailTemplates:
    """Create stunning professional emails with proper branding"""
    
    BRAND_COLOR_PRIMARY = "#FFC107"  # Gold/Yellow from logo
    BRAND_COLOR_DARK = "#1a1a1a"     # Dark background
    BRAND_COLOR_ACCENT = "#FF6B6B"   # Accent red
    BRAND_COLOR_SUCCESS = "#4CAF50"  # Success green
    
    @staticmethod
    def get_header_with_logo():
        """Stunning header with logo and branding"""
        return """
        <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 40px 20px; text-align: center; border-bottom: 4px solid #FFC107;">
            <div style="max-width: 600px; margin: 0 auto;">
                <img src="https://tickethouse.net/static/images/logoDarkbg.png" alt="TicketHouse" style="height: 80px; margin-bottom: 20px;">
                <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 900; letter-spacing: 1px;">TICKETHOUSE</h1>
                <p style="color: #FFC107; margin: 8px 0 0 0; font-size: 14px; font-weight: 600; letter-spacing: 2px;">PREMIUM TICKET MARKETPLACE</p>
            </div>
        </div>
        """
    
    @staticmethod
    def get_footer():
        """Professional footer with branding"""
        return """
        <div style="background-color: #1a1a1a; color: white; padding: 40px 20px; text-align: center; border-top: 2px solid #FFC107;">
            <div style="max-width: 600px; margin: 0 auto;">
                <p style="margin: 0 0 15px 0; font-size: 14px;">
                    <strong>TicketHouse</strong> | Your Premium Ticket Marketplace
                </p>
                <div style="margin: 15px 0; padding: 15px 0; border-top: 1px solid #333; border-bottom: 1px solid #333;">
                    <a href="https://tickethouse.net" style="color: #FFC107; text-decoration: none; margin: 0 15px; font-size: 13px; font-weight: 600;">Website</a>
                    <a href="https://tickethouse.net/support" style="color: #FFC107; text-decoration: none; margin: 0 15px; font-size: 13px; font-weight: 600;">Support</a>
                    <a href="mailto:support@tickethouse.net" style="color: #FFC107; text-decoration: none; margin: 0 15px; font-size: 13px; font-weight: 600;">Contact</a>
                </div>
                <p style="color: #888; font-size: 11px; margin: 15px 0 0 0;">
                    © 2026 TicketHouse. All rights reserved.<br>
                    <a href="https://tickethouse.net/terms" style="color: #FFC107; text-decoration: none;">Terms of Service</a> | 
                    <a href="https://tickethouse.net/privacy" style="color: #FFC107; text-decoration: none;">Privacy Policy</a>
                </p>
            </div>
        </div>
        """
    
    @staticmethod
    def get_hero_section(title, subtitle, icon_emoji="🎉"):
        """Exciting hero section with title and subtitle"""
        return f"""
        <div style="background: linear-gradient(135deg, #FFC107 0%, #FFB300 100%); padding: 40px 20px; text-align: center; color: white;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="font-size: 48px; margin-bottom: 15px;">{icon_emoji}</div>
                <h2 style="color: white; margin: 0 0 10px 0; font-size: 28px; font-weight: 900;">{title}</h2>
                <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 16px; line-height: 1.5;">{subtitle}</p>
            </div>
        </div>
        """
    
    @staticmethod
    def get_detail_box(label, value, icon=""):
        """Beautiful detail box with icon"""
        return f"""
        <div style="background: #f8f9fa; border-left: 4px solid #FFC107; padding: 15px; margin: 10px 0; border-radius: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p style="color: #666; font-size: 12px; margin: 0 0 5px 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">{icon} {label}</p>
                    <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 700;">{value}</p>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def get_cta_button(text, url, style="primary"):
        """Beautiful call-to-action button"""
        if style == "primary":
            bg_color = "#FFC107"
            text_color = "#1a1a1a"
        else:
            bg_color = "#1a1a1a"
            text_color = "#FFC107"
        
        return f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{url}" style="background-color: {bg_color}; color: {text_color}; padding: 16px 40px; text-decoration: none; border-radius: 50px; font-weight: 900; display: inline-block; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3); transition: all 0.3s ease;">
                {text}
            </a>
        </div>
        """
    
    @staticmethod
    def payment_successful_buyer(order, ticket):
        """STUNNING payment success email for buyer"""
        details_html = ""
        details = [
            ("🎫", "Event", order.event_name),
            ("📅", "Date", order.event_date.strftime('%B %d, %Y')),
            ("🕐", "Time", order.event_time.strftime('%I:%M %p')),
            ("📍", "Section", order.ticket_section),
            ("🪑", "Row", order.ticket_row),
            ("🎟️", "Seats", ', '.join(order.ticket_seats)),
            ("📊", "Quantity", str(order.number_of_tickets)),
            ("🔐", "Order ID", str(order.order_number) if order.order_number else str(order.id)[:8]),
        ]
        
        for icon, label, value in details:
            details_html += ProfessionalEmailTemplates.get_detail_box(label, value, icon)
        
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; color: #333; line-height: 1.6; }}
                a {{ color: #FFC107; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f5f5f5;">
            <div class="container" style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
                {ProfessionalEmailTemplates.get_header_with_logo()}
                
                {ProfessionalEmailTemplates.get_hero_section('🎉 Payment Successful!', 'Your tickets are now secured. Get ready for an amazing experience!', '✅')}
                
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #1a1a1a; margin: 0 0 30px 0;">
                        Hey <strong>{order.buyer.first_name or 'there'}</strong>! 👋<br><br>
                        Your payment has been processed successfully. Your tickets are confirmed and ready to go!
                    </p>
                    
                    <h3 style="color: #1a1a1a; font-size: 18px; margin: 30px 0 20px 0; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">📋 Your Ticket Details</h3>
                    {details_html}
                    
                    <div style="background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%); border-left: 4px solid #4CAF50; padding: 20px; margin: 30px 0; border-radius: 4px;">
                        <p style="color: #2e7d32; font-weight: 900; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">📎 Ticket Attachments</p>
                        <p style="color: #558b2f; margin: 0; font-size: 14px;">Your ticket PDFs are attached to this email. Download and save them securely.</p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-left: 4px solid #FF9800; padding: 20px; margin: 30px 0; border-radius: 4px;">
                        <p style="color: #e65100; font-weight: 900; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">💡 Pro Tips</p>
                        <ul style="color: #bf360c; margin: 0; padding-left: 20px; font-size: 13px;">
                            <li>Save your ticket PDFs to your phone for easy access</li>
                            <li>Arrive early to avoid queues at the venue</li>
                            <li>Check the event details for any special instructions</li>
                        </ul>
                    </div>
                    
                    {ProfessionalEmailTemplates.get_cta_button('View Your Orders', 'https://tickethouse.net/my-orders/')}
                    
                    <hr style="border: none; border-top: 2px solid #f0f0f0; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 13px; line-height: 1.6; margin: 0;">
                        <strong>Need Help?</strong> Our support team is available 24/7. Reach out to us at 
                        <a href="mailto:support@tickethouse.net" style="color: #FFC107; text-decoration: none;">support@tickethouse.net</a>
                    </p>
                </div>
                
                {ProfessionalEmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def payment_successful_seller(order, ticket):
        """STUNNING payment success email for seller"""
        details_html = ""
        details = [
            ("🎫", "Event", order.event_name),
            ("🎟️", "Ticket ID", str(ticket.ticket_number) if ticket.ticket_number else str(ticket.ticket_id)),
            ("📍", "Section", order.ticket_section),
            ("📊", "Quantity Sold", str(order.number_of_tickets)),
            ("💰", "Amount", f"£{order.amount:.2f}"),
        ]
        
        for icon, label, value in details:
            details_html += ProfessionalEmailTemplates.get_detail_box(label, value, icon)
        
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
                {ProfessionalEmailTemplates.get_header_with_logo()}
                
                {ProfessionalEmailTemplates.get_hero_section('🎉 Ticket Sold!', 'Congratulations! Your ticket has been purchased. Payment is on the way!', '💰')}
                
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #1a1a1a; margin: 0 0 30px 0;">
                        Hey <strong>{ticket.seller.first_name or 'Seller'}</strong>! 🎊<br><br>
                        Great news! Your ticket has been successfully sold. A buyer has purchased your listing!
                    </p>
                    
                    <h3 style="color: #1a1a1a; font-size: 18px; margin: 30px 0 20px 0; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">📊 Sale Details</h3>
                    {details_html}
                    
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-left: 4px solid #2196f3; padding: 20px; margin: 30px 0; border-radius: 4px;">
                        <p style="color: #1565c0; font-weight: 900; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">📋 Next Steps</p>
                        <p style="color: #0d47a1; margin: 0; font-size: 14px;">Ensure your ticket PDF is uploaded for verification. Payment will be processed once verified!</p>
                    </div>
                    
                    {ProfessionalEmailTemplates.get_cta_button('View Your Sales', 'https://tickethouse.net/my-sales/')}
                    
                    <hr style="border: none; border-top: 2px solid #f0f0f0; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 13px; line-height: 1.6; margin: 0;">
                        <strong>Questions?</strong> Contact our support team at 
                        <a href="mailto:support@tickethouse.net" style="color: #FFC107; text-decoration: none;">support@tickethouse.net</a>
                    </p>
                </div>
                
                {ProfessionalEmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def ticket_listing_confirmation(ticket, seller_email, marketplace_url):
        """STUNNING ticket listing confirmation"""
        details_html = ""
        details = [
            ("🎫", "Event", ticket.event.name),
            ("🎟️", "Ticket ID", str(ticket.ticket_number) if ticket.ticket_number else str(ticket.ticket_id)),
            ("📍", "Section", ticket.section.name),
            ("🪑", "Seats", ', '.join(ticket.seats) if ticket.seats else "N/A"),
            ("💷", "Price", f"£{ticket.sell_price:.2f}"),
            ("📊", "Quantity", str(ticket.number_of_tickets)),
        ]
        
        for icon, label, value in details:
            details_html += ProfessionalEmailTemplates.get_detail_box(label, value, icon)
        
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
                {ProfessionalEmailTemplates.get_header_with_logo()}
                
                {ProfessionalEmailTemplates.get_hero_section('🚀 Listing Live!', 'Your tickets are now visible to thousands of buyers on TicketHouse!', '✨')}
                
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #1a1a1a; margin: 0 0 30px 0;">
                        Your ticket listing is now <strong>LIVE</strong> on the marketplace! 🎯<br><br>
                        Buyers can now see your listing and make purchases. Here are the details:
                    </p>
                    
                    <h3 style="color: #1a1a1a; font-size: 18px; margin: 30px 0 20px 0; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">🎫 Listing Details</h3>
                    {details_html}
                    
                    <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); border-left: 4px solid #9c27b0; padding: 20px; margin: 30px 0; border-radius: 4px;">
                        <p style="color: #6a1b9a; font-weight: 900; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">💡 Maximize Your Sales</p>
                        <ul style="color: #4a148c; margin: 0; padding-left: 20px; font-size: 13px;">
                            <li>Price competitively to attract buyers</li>
                            <li>Respond quickly to buyer inquiries</li>
                            <li>Upload high-quality ticket images</li>
                        </ul>
                    </div>
                    
                    {ProfessionalEmailTemplates.get_cta_button('View Your Listing', marketplace_url)}
                    
                    <hr style="border: none; border-top: 2px solid #f0f0f0; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 13px; line-height: 1.6; margin: 0;">
                        <strong>Good luck!</strong> We're excited to help you sell your tickets. Contact us at 
                        <a href="mailto:support@tickethouse.net" style="color: #FFC107; text-decoration: none;">support@tickethouse.net</a> if you need any help.
                    </p>
                </div>
                
                {ProfessionalEmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def payment_failed(order):
        """STUNNING payment failed email"""
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
                {ProfessionalEmailTemplates.get_header_with_logo()}
                
                {ProfessionalEmailTemplates.get_hero_section('Payment Issue', 'We had trouble processing your payment. Let\\'s get this fixed!', '⚠️')}
                
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #1a1a1a; margin: 0 0 30px 0;">
                        Hi <strong>{order.buyer.first_name or 'there'}</strong>,<br><br>
                        Unfortunately, we couldn't process your payment. But don't worry—it's usually a quick fix!
                    </p>
                    
                    <h3 style="color: #1a1a1a; font-size: 18px; margin: 30px 0 20px 0; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">🔍 Order Details</h3>
                    {ProfessionalEmailTemplates.get_detail_box('Event', order.event_name, '🎫')}
                    {ProfessionalEmailTemplates.get_detail_box('Amount', f'£{order.amount:.2f}', '💷')}
                    {ProfessionalEmailTemplates.get_detail_box('Order ID', str(order.order_number) if order.order_number else str(order.id)[:8], '🔐')}
                    
                    <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-left: 4px solid #f44336; padding: 20px; margin: 30px 0; border-radius: 4px;">
                        <p style="color: #c62828; font-weight: 900; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">🛠️ Common Solutions</p>
                        <ul style="color: #b71c1c; margin: 0; padding-left: 20px; font-size: 13px;">
                            <li>Check your card details and try again</li>
                            <li>Ensure you have sufficient funds</li>
                            <li>Contact your bank if issues persist</li>
                            <li>Try a different payment method</li>
                        </ul>
                    </div>
                    
                    {ProfessionalEmailTemplates.get_cta_button('Try Payment Again', 'https://tickethouse.net/my-orders/')}
                    
                    <hr style="border: none; border-top: 2px solid #f0f0f0; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 13px; line-height: 1.6; margin: 0;">
                        <strong>Still having issues?</strong> Our support team is here to help! Email us at 
                        <a href="mailto:support@tickethouse.net" style="color: #FFC107; text-decoration: none;">support@tickethouse.net</a>
                    </p>
                </div>
                
                {ProfessionalEmailTemplates.get_footer()}
            </div>
        </body>
        </html>
        """
        return html_content
    
    @staticmethod
    def send_html_email(subject, html_content, recipient_email, attachments=None):
        """Send stunning HTML email with optional attachments"""
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
            logger.info(f"✓ Professional email sent to {recipient_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to send email to {recipient_email}: {str(e)}")
            return False
